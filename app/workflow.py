from datetime import timedelta
from temporalio import activity, workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from app.database import get_db
    from app.models import ShiftFanoutStatus
    from app.notifier import place_phone_call


@activity.defn
async def escalate_shift_activity(shift_id: str) -> str:
    """Activity that performs the actual phone-call escalation."""
    db = get_db()
    fanout = db.fanouts.get(shift_id)

    if fanout is None or fanout.status != ShiftFanoutStatus.PENDING:
        return "already_claimed_or_missing"

    shift = db.shifts.get(shift_id)
    if shift is None:
        return "shift_not_found"

    matching_caregivers = db.get_caregivers_by_role(shift.role_required)
    message = (
        f"Shift still available: {shift.start_time.strftime('%Y-%m-%d %H:%M')} "
        f"to {shift.end_time.strftime('%Y-%m-%d %H:%M')}. "
        f"Reply 'yes' or 'accept' to claim."
    )

    for caregiver in matching_caregivers:
        await place_phone_call(caregiver.phone, message)

    from datetime import UTC, datetime
    fanout.status = ShiftFanoutStatus.ESCALATED
    fanout.phone_call_sent_at = datetime.now(UTC)
    db.fanouts.put(shift_id, fanout)

    return f"escalated_to_{len(matching_caregivers)}_caregivers"


@workflow.defn
class ShiftEscalationWorkflow:
    """Waits 10 minutes, then escalates if the shift is still pending."""

    @workflow.run
    async def run(self, shift_id: str) -> str:
        # Wait 10 minutes (for demos you can lower this)
        await workflow.sleep(timedelta(minutes=10))

        result = await workflow.execute_activity(
            escalate_shift_activity,
            shift_id,
            start_to_close_timeout=timedelta(seconds=60),
            retry_policy=RetryPolicy(maximum_attempts=3),
        )
        return result