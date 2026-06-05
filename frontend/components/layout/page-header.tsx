import Link from 'next/link';
import { PlusActionButton } from '@/components/layout/plus-action-button';

type PageHeaderProps = {
  title: string;
  subtitle: string;
  actionLabel?: string;
  actionHref?: string;
};

export function PageHeader({
  title,
  subtitle,
  actionLabel = 'Новый проект',
  actionHref,
}: PageHeaderProps) {
  return (
    <div className="mb-6 flex flex-col gap-4 md:flex-row md:justify-between">
      <div>
        <h2 className="text-3xl font-semibold">{title}</h2>
        <p className="text-sm text-muted-foreground">{subtitle}</p>
      </div>

      {actionHref ? (
        <Link
          href={actionHref}
          className="inline-flex h-10 items-center justify-center rounded-2xl bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
        >
          {actionLabel}
        </Link>
      ) : (
        <PlusActionButton label={actionLabel} />
      )}
    </div>
  );
}