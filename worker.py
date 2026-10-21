import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

from app.workflows import ShiftEscalationWorkflow, escalate_shift_activity


async def main():
    client = await Client.connect("localhost:7233")

    worker = Worker(
        client,
        task_queue="shift-escalation",
        workflows=[ShiftEscalationWorkflow],
        activities=[escalate_shift_activity],
    )
    print("Temporal worker started on task queue: shift-escalation")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())