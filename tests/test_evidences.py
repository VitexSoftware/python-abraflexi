"""
Tests for the concrete FakturaVydana and Adresar evidence classes.
"""

import json
from datetime import date, timedelta
from unittest.mock import MagicMock

from python_abraflexi.evidences import Adresar, FakturaVydana


def _fake_response(payload, status_code=201):
    response = MagicMock()
    response.status_code = status_code
    response.content = json.dumps(payload).encode("utf-8")
    response.json.return_value = payload
    return response


def _base_options(**overrides):
    options = {
        "url": "https://demo.flexibee.eu",
        "company": "demo",
        "user": "winstrom",
        "password": "winstrom",
        "offline": False,
        "autoload": False,
    }
    options.update(overrides)
    return options


class TestFakturaVydanaEvidence:
    def test_evidence_name(self):
        invoice = FakturaVydana(None, _base_options(offline=True))
        assert invoice.evidence == "faktura-vydana"

    def test_match_payment_builds_sparovani_structure(self):
        invoice = FakturaVydana(None, _base_options())
        invoice.my_key = 1

        payer = FakturaVydana(None, _base_options())
        payer.evidence = "banka"
        payer.my_key = 55
        payer.session.put = MagicMock(
            return_value=_fake_response({"winstrom": {"results": [{"id": "55"}]}})
        )

        assert invoice.match_payment(payer, zbytek="zauctovat") is True

        sent_body = json.loads(payer.session.put.call_args.kwargs["data"])
        sparovani = sent_body["winstrom"]["banka"]["sparovani"]
        assert sparovani["uhrazovanaFak"] == "1"
        assert sparovani["uhrazovanaFak@type"] == "faktura-vydana"
        assert sparovani["zbytek"] == "zauctovat"

    def test_match_payment_with_overpayment_type(self):
        invoice = FakturaVydana(None, _base_options())
        invoice.my_key = 1
        payer = FakturaVydana(None, _base_options())
        payer.evidence = "banka"
        payer.my_key = 55
        payer.session.put = MagicMock(
            return_value=_fake_response({"winstrom": {"results": [{"id": "55"}]}})
        )

        invoice.match_payment(payer, overpay_to="PREPLATEK")

        sent_body = json.loads(payer.session.put.call_args.kwargs["data"])
        assert (
            sent_body["winstrom"]["banka"]["preplatek"]["typDokl"] == "code:PREPLATEK"
        )

    def test_cash_payment_defaults_and_castka(self):
        invoice = FakturaVydana(None, _base_options())
        invoice.my_key = 1
        invoice.session.put = MagicMock(
            return_value=_fake_response({"winstrom": {"results": [{"id": "1"}]}})
        )

        assert invoice.cash_payment(1500) is True

        sent_body = json.loads(invoice.session.put.call_args.kwargs["data"])
        uhrada = sent_body["winstrom"]["faktura-vydana"]["hotovostni-uhrada"]
        assert uhrada["castka"] == 1500
        assert uhrada["pokladna"] == "code:POKLADNA KČ"
        assert uhrada["typDokl"] == "code:STANDARD"
        assert uhrada["kurzKDatuUhrady"] is False

    def test_link_zdd_builds_bond_request(self):
        invoice = FakturaVydana(None, _base_options())
        invoice.my_key = 1
        invoice.session.put = MagicMock(
            return_value=_fake_response({"winstrom": {"results": [{"id": "1"}]}})
        )

        income = FakturaVydana(None, _base_options())
        income.evidence = "banka"
        income.my_key = 9

        assert invoice.link_zdd(income) is True

        sent_body = json.loads(invoice.session.put.call_args.kwargs["data"])
        bond = sent_body["winstrom"]["faktura-vydana"]["vytvor-vazbu-zdd"]
        assert bond["uhrada"] == "9"
        assert bond["uhrada@type"] == "banka"

    def test_overdue_days_positive_for_past_due_date(self):
        due = date.today() - timedelta(days=5)
        assert FakturaVydana.overdue_days(due) == 5

    def test_overdue_days_negative_for_future_due_date(self):
        due = date.today() + timedelta(days=3)
        assert FakturaVydana.overdue_days(due) == -3

    def test_overdue_days_accepts_iso_string(self):
        due = (date.today() - timedelta(days=2)).isoformat()
        assert FakturaVydana.overdue_days(due) == 2


class TestAdresarEvidence:
    def test_evidence_name(self):
        adresar = Adresar(None, _base_options(offline=True))
        assert adresar.evidence == "adresar"

    def test_get_notification_email_address_uses_own_email(self):
        adresar = Adresar(None, _base_options())
        adresar.session.get = MagicMock(
            return_value=_fake_response(
                {
                    "winstrom": {
                        "results": [
                            {"id": "1", "email": "firm@example.com", "kontakty": []}
                        ]
                    }
                },
                status_code=200,
            )
        )
        assert adresar.get_notification_email_address() == "firm@example.com"

    def test_get_notification_email_address_prefers_primary_contact(self):
        adresar = Adresar(None, _base_options())
        adresar.session.get = MagicMock(
            return_value=_fake_response(
                {
                    "winstrom": {
                        "results": [
                            {
                                "id": "1",
                                "email": "firm@example.com",
                                "kontakty": [
                                    {"primarni": "false", "email": "other@example.com"},
                                    {
                                        "primarni": "true",
                                        "email": "primary@example.com",
                                    },
                                ],
                            }
                        ]
                    }
                },
                status_code=200,
            )
        )
        assert adresar.get_notification_email_address() == "primary@example.com"

    def test_get_notification_email_address_purpose_matching(self):
        adresar = Adresar(None, _base_options())
        adresar.session.get = MagicMock(
            return_value=_fake_response(
                {
                    "winstrom": {
                        "results": [
                            {
                                "id": "1",
                                "email": "",
                                "kontakty": [
                                    {
                                        "primarni": "false",
                                        "email": "sales@example.com",
                                        "odesilatObj": "true",
                                    }
                                ],
                            }
                        ]
                    }
                },
                status_code=200,
            )
        )
        assert (
            adresar.get_notification_email_address(purpose="Obj") == "sales@example.com"
        )

    def test_get_email_delegates_to_notification_email(self):
        adresar = Adresar(None, _base_options())
        adresar.session.get = MagicMock(
            return_value=_fake_response(
                {"winstrom": {"results": [{"id": "1", "email": "x@example.com"}]}},
                status_code=200,
            )
        )
        assert adresar.get_email() == "x@example.com"

    def test_get_sum_from_abraflexi_returns_empty(self):
        adresar = Adresar(None, _base_options(offline=True))
        assert adresar.get_sum_from_abraflexi() == {}

    def test_get_bank_account_number_uses_get_columns(self):
        adresar = Adresar(None, _base_options())
        adresar.my_key = 1
        adresar.session.get = MagicMock(
            return_value=_fake_response(
                {"winstrom": {"results": [{"buc": "123456", "smerKod": "0100"}]}},
                status_code=200,
            )
        )
        result = adresar.get_bank_account_number()
        assert result == [{"buc": "123456", "smerKod": "0100"}]
        called_url = adresar.session.get.call_args.args[0]
        assert "adresar-bankovni-ucet" in called_url
