import { Card } from "@/components/ui/card";

export function DraftMessages({
  prescriberMessage,
  patientMessage
}: {
  prescriberMessage: string;
  patientMessage: string;
}) {
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <Card>
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slateblue">
          Draft Prescriber Message
        </p>
        <p className="mt-4 whitespace-pre-wrap text-sm leading-7 text-ink/85">
          {prescriberMessage}
        </p>
      </Card>
      <Card>
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slateblue">
          Draft Patient Message
        </p>
        <p className="mt-4 whitespace-pre-wrap text-sm leading-7 text-ink/85">
          {patientMessage}
        </p>
      </Card>
    </div>
  );
}
