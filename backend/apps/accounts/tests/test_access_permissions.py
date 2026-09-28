import pytest

from apps.accounts.access_permissions import (
    AccessPermission,
    get_user_permissions,
    user_has_permission,
)
from apps.accounts.models import User, UserRole

P = AccessPermission


def _user(role: UserRole, *, is_active: bool = True) -> User:
    return User(username=f"u-{role}", role=role, is_active=is_active)


@pytest.mark.parametrize(
    "permission",
    [
        P.PATIENT_CREATE,
        P.APPOINTMENT_VIEW,
        P.CHECKIN_CREATE,
        P.RECEPTION_QUEUE_VIEW,
        P.RECEPTION_QUEUE_CALL,
        P.WORK_SESSION_RECEPTION_DESK,
    ],
)
def test_atendente_has_administrative_reception_permissions(permission):
    assert user_has_permission(_user(UserRole.ATENDENTE), permission)


@pytest.mark.parametrize(
    "permission",
    [
        P.MEDICAL_RECORD_VIEW_ACTIVE_PATIENT,
        P.MEDICAL_RECORD_VIEW_ANY,
        P.BILLING_VIEW_HISTORY,
        P.CLINICAL_QUEUE_VIEW_OWN,
        P.CLINICAL_QUEUE_VIEW_ALL,
        P.CLINICAL_QUEUE_CALL_OWN,
        P.CLINICAL_QUEUE_CALL_ANY,
        P.WORK_SESSION_CONSULTATION_ROOM,
        P.REPORTS_VIEW_ALL,
        P.USERS_MANAGE,
        P.AUDIT_VIEW,
    ],
)
def test_atendente_has_no_clinical_financial_or_admin_permissions(permission):
    assert not user_has_permission(_user(UserRole.ATENDENTE), permission)


@pytest.mark.parametrize(
    "permission",
    [
        P.CLINICAL_QUEUE_VIEW_OWN,
        P.CLINICAL_QUEUE_VIEW_INACTIVE_OWN,
        P.CLINICAL_QUEUE_CALL_OWN,
        P.MEDICAL_RECORD_VIEW_ACTIVE_PATIENT,
        P.ENCOUNTER_COMPLETE_OWN,
        P.WORK_SESSION_CONSULTATION_ROOM,
    ],
)
def test_medico_has_own_clinical_queue_permissions(permission):
    assert user_has_permission(_user(UserRole.MEDICO), permission)


@pytest.mark.parametrize(
    "permission",
    [
        P.PATIENT_CREATE,
        P.CHECKIN_CREATE,
        P.RECEPTION_QUEUE_VIEW,
        P.RECEPTION_QUEUE_CALL,
        P.CLINICAL_QUEUE_VIEW_ALL,
        P.CLINICAL_QUEUE_CALL_ANY,
        P.MEDICAL_RECORD_VIEW_ANY,
        P.BILLING_VIEW_HISTORY,
        P.REPORTS_VIEW_ALL,
        P.AUDIT_VIEW,
    ],
)
def test_medico_has_no_reception_financial_or_global_permissions(permission):
    assert not user_has_permission(_user(UserRole.MEDICO), permission)


def test_gestor_has_every_administrative_permission():
    permissions = get_user_permissions(_user(UserRole.GESTOR))

    assert {
        P.PATIENT_CREATE,
        P.CLINICAL_QUEUE_VIEW_ALL,
        P.MEDICAL_RECORD_VIEW_ANY,
        P.BILLING_VIEW_HISTORY,
        P.REPORTS_VIEW_ALL,
        P.USERS_MANAGE,
        P.AUDIT_VIEW,
    } <= permissions


def test_gestor_does_not_register_clinical_acts():
    gestor = _user(UserRole.GESTOR)

    assert not user_has_permission(gestor, P.MEDICAL_RECORD_UPDATE_ACTIVE_PATIENT)
    assert not user_has_permission(gestor, P.ENCOUNTER_COMPLETE_OWN)


def test_inactive_user_has_no_permissions():
    assert get_user_permissions(_user(UserRole.GESTOR, is_active=False)) == frozenset()
