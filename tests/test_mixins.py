"""
Tests for the reusable evidence mixins (ports of the PHP AbraFlexi traits).
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from python_abraflexi import ReadWrite
from python_abraflexi.mixins import (
    EmailMixin,
    FirmaMixin,
    LabelsMixin,
    LockMixin,
    RecordChangesMixin,
    SubItemsMixin,
    SumMixin,
)


def _fake_response(payload, status_code=200):
    response = MagicMock()
    response.status_code = status_code
    response.content = json.dumps(payload).encode("utf-8")
    response.json.return_value = payload
    return response


class _LabeledThing(LabelsMixin, ReadWrite):
    def __init__(self, init=None, options=None):
        super().__init__(init, {**(options or {}), "evidence": "cenik"})


class _SubItemThing(SubItemsMixin, ReadWrite):
    def __init__(self, init=None, options=None):
        super().__init__(init, {**(options or {}), "evidence": "faktura-vydana"})


class _SumThing(SumMixin, ReadWrite):
    def __init__(self, init=None, options=None):
        super().__init__(init, {**(options or {}), "evidence": "cenik"})


class _ChangesThing(RecordChangesMixin, ReadWrite):
    def __init__(self, init=None, options=None):
        super().__init__(init, {**(options or {}), "evidence": "adresar"})


class _LockThing(LockMixin, ReadWrite):
    def __init__(self, init=None, options=None):
        super().__init__(init, {**(options or {}), "evidence": "faktura-vydana"})


class _FirmaThing(FirmaMixin, ReadWrite):
    def __init__(self, init=None, options=None):
        super().__init__(init, {**(options or {}), "evidence": "faktura-vydana"})


class FakLikeDoc(EmailMixin, ReadWrite):
    def __init__(self, init=None, options=None):
        super().__init__(init, {**(options or {}), "evidence": "faktura-vydana"})


class PoptavkaLikeDoc(EmailMixin, ReadWrite):
    def __init__(self, init=None, options=None):
        super().__init__(init, {**(options or {}), "evidence": "poptavka-vydana"})


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


class TestLabelsMixin:
    def test_get_labels_parses_comma_separated_string(self):
        thing = _LabeledThing(None, _base_options())
        thing.set_data_value("stitky", "VIP, DULEZITE")
        assert thing.get_labels() == ["VIP", "DULEZITE"]

    def test_get_labels_empty_when_unset(self):
        thing = _LabeledThing(None, _base_options())
        assert thing.get_labels() == []

    def test_set_label_success(self):
        thing = _LabeledThing(None, _base_options())
        thing.my_key = 1
        thing.session.put = MagicMock(
            return_value=_fake_response(
                {"winstrom": {"success": "true", "results": [{"id": "1"}]}},
                status_code=201,
            )
        )
        assert thing.set_label("code:VIP") is True

    def test_unset_label_keeps_remaining_labels(self):
        thing = _LabeledThing(None, _base_options())
        thing.my_key = 1
        thing.set_data_value("stitky", ["VIP", "DULEZITE"])
        thing.session.put = MagicMock(
            return_value=_fake_response(
                {"winstrom": {"success": "true", "results": [{"id": "1"}]}},
                status_code=201,
            )
        )
        assert thing.unset_label("VIP") is True
        sent_body = json.loads(thing.session.put.call_args.kwargs["data"])
        assert sent_body["winstrom"]["cenik"]["stitky"] == ["DULEZITE"]
        assert sent_body["winstrom"]["cenik"]["stitky@removeAll"] == "true"

    def test_unset_labels_sends_remove_all_without_stitky(self):
        thing = _LabeledThing(None, _base_options())
        thing.my_key = 1
        thing.session.put = MagicMock(
            return_value=_fake_response(
                {"winstrom": {"success": "true", "results": [{"id": "1"}]}},
                status_code=201,
            )
        )
        assert thing.unset_labels() is True
        sent_body = json.loads(thing.session.put.call_args.kwargs["data"])
        assert "stitky" not in sent_body["winstrom"]["cenik"]
        assert sent_body["winstrom"]["cenik"]["stitky@removeAll"] == "true"


class TestSubItemsMixin:
    def test_get_sub_menu_name_detects_polozky_faktury(self):
        thing = _SubItemThing(None, _base_options())
        thing.take_data({"id": 1, "polozkyFaktury": []})
        assert thing.get_sub_menu_name() == "polozkyFaktury"

    def test_get_sub_menu_name_none_when_absent(self):
        thing = _SubItemThing(None, _base_options())
        thing.take_data({"id": 1})
        assert thing.get_sub_menu_name() is None

    def test_set_and_get_sub_items(self):
        thing = _SubItemThing(None, _base_options())
        thing.take_data({"id": 1, "polozkyFaktury": []})
        thing.set_sub_items([{"nazev": "Item 1"}])
        assert thing.get_sub_items() == [{"nazev": "Item 1"}]

    def test_add_array_to_branch_appends(self):
        thing = _SubItemThing(None, _base_options())
        thing.take_data({"id": 1, "polozkyFaktury": [{"nazev": "Existing"}]})
        thing.add_array_to_branch({"nazev": "New"})
        assert thing.get_data_value("polozkyFaktury") == [
            {"nazev": "Existing"},
            {"nazev": "New"},
        ]

    def test_add_array_to_branch_remove_all_flag(self):
        thing = _SubItemThing(None, _base_options())
        thing.take_data({"id": 1})
        thing.add_array_to_branch({"nazev": "New"}, remove_all=True)
        assert thing.get_data_value("polozkyDokladu@removeAll") == "true"


class TestSumMixin:
    def test_get_sum_from_abraflexi(self):
        thing = _SumThing(None, _base_options())
        thing.session.get = MagicMock(
            return_value=_fake_response({"winstrom": {"sum": {"sumCelkem": "100"}}})
        )
        assert thing.get_sum_from_abraflexi() == {"sumCelkem": "100"}
        called_url = thing.session.get.call_args.args[0]
        assert "$sum" in called_url


class TestRecordChangesMixin:
    def test_requires_record_identifier(self):
        thing = _ChangesThing(None, _base_options())
        with pytest.raises(ValueError):
            thing.get_record_changes()

    def test_get_record_changes_unwraps_zmeny(self):
        thing = _ChangesThing(None, _base_options())
        thing.my_key = 1
        thing.session.get = MagicMock(
            return_value=_fake_response(
                {"winstrom": {"zmeny": [{"pole": "nazev", "puvHodnota": "A"}]}}
            )
        )
        changes = thing.get_record_changes()
        assert changes == [{"pole": "nazev", "puvHodnota": "A"}]
        assert thing.session.get.call_args.args[0].endswith("/adresar/1/zmeny.json")


class TestLockMixin:
    def test_is_locked_requires_zamekk(self):
        thing = _LockThing(None, _base_options())
        with pytest.raises(ValueError):
            thing.is_locked()

    def test_is_locked_true_when_not_open(self):
        thing = _LockThing(None, _base_options())
        thing.set_data_value("zamekK", "zamek.uzamceno")
        assert thing.is_locked() is True

    def test_is_locked_false_when_open(self):
        thing = _LockThing(None, _base_options())
        thing.set_data_value("zamekK", "zamek.otevreno")
        assert thing.is_locked() is False

    def test_get_lock_type_strips_prefix(self):
        thing = _LockThing(None, _base_options())
        thing.set_data_value("zamekK", "zamek.uzamceno")
        assert thing.get_lock_type() == "uzamceno"

    def test_lock_and_unlock_send_action_attribute(self):
        thing = _LockThing(None, _base_options())
        thing.my_key = 1
        thing.session.post = MagicMock(
            return_value=_fake_response(
                {"winstrom": {"success": "true", "results": [{"id": "1"}]}}
            )
        )
        assert thing.lock()
        sent_body = json.loads(thing.session.post.call_args.kwargs["data"])
        assert sent_body["winstrom"]["faktura-vydana"]["@action"] == "lock"
        assert sent_body["winstrom"]["faktura-vydana"]["id"] == "1"

        assert thing.unlock()
        sent_body = json.loads(thing.session.post.call_args.kwargs["data"])
        assert sent_body["winstrom"]["faktura-vydana"]["@action"] == "unlock"


class TestFirmaMixin:
    def test_get_firma_object_returns_cached_adresar(self):
        thing = _FirmaThing(None, _base_options(offline=True))
        thing.set_data_value("firma", "code:FIRMA")

        from python_abraflexi.evidences.adresar import Adresar

        firma1 = thing.get_firma_object()
        firma2 = thing.get_firma_object()

        assert isinstance(firma1, Adresar)
        assert firma1 is firma2


class TestEmailMixin:
    def test_get_email_prefers_kontakt_email(self):
        doc = FakLikeDoc(None, _base_options(offline=True))
        doc.set_data_value("kontaktEmail", "direct@example.com")
        assert doc.get_email() == "direct@example.com"

    def test_get_email_falls_back_to_addresser(self):
        doc = FakLikeDoc(None, _base_options(offline=True))
        doc.set_data_value("firma", "code:FIRMA")
        with patch(
            "python_abraflexi.evidences.adresar.Adresar.get_notification_email_address",
            return_value="fallback@example.com",
        ):
            assert doc.get_email() == "fallback@example.com"

    def test_get_recipients_combines_and_dedupes(self):
        doc = FakLikeDoc(None, _base_options(offline=True))
        doc.set_data_value("kontaktEmail", "a@example.com")
        doc.set_data_value("email", "a@example.com")
        doc.set_data_value("firma", "code:FIRMA")
        with patch(
            "python_abraflexi.evidences.adresar.Adresar.get_notification_email_address",
            return_value="b@example.com,c@example.com",
        ):
            assert doc.get_recipients() == "a@example.com,b@example.com,c@example.com"

    def test_doc_type_to_purpose_faktura(self):
        doc = FakLikeDoc(None, _base_options(offline=True))
        assert doc._doc_type_to_purpose() == "Fak"

    def test_doc_type_to_purpose_poptavka_maps_to_ppt(self):
        doc = PoptavkaLikeDoc(None, _base_options(offline=True))
        assert doc._doc_type_to_purpose() == "Ppt"
