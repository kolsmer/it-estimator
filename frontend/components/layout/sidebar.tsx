import Link from 'next/link';
import { Archive, BarChart3, Briefcase, Calculator, Sparkles } from 'lucide-react';

const navItems = [
  { href: '/dashboard', label: 'Дашборд', icon: BarChart3 },
  { href: '/projects', label: 'Проекты', icon: Briefcase },
  { href: '/roles', label: 'Роли и ставки', icon: Calculator },
  { href: '/archive', label: 'Архив', icon: Archive },
];

export function Sidebar() {
  return (
    <aside className="sticky top-0 flex h-screen w-80 flex-col border-r border-border/70 bg-slate-950/70 p-6 backdrop-blur">
      <div className="mb-8 flex items-center gap-3">
        <div className="rounded-2xl bg-violet-500/10 p-2 text-violet-300">
          <Sparkles className="h-5 w-5" />
        </div>
        <div>
          <h1 className="text-xl font-semibold">IT Estimator</h1>
          <p className="text-sm text-muted-foreground">Оценка проектов</p>
        </div>
      </div>

      <nav className="flex flex-col gap-2">
        {navItems.map((item) => {
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className="flex items-center gap-3 rounded-xl px-3 py-2 text-sm text-muted-foreground transition hover:bg-muted/40 hover:text-foreground"
            >
              <Icon className="h-4 w-4" />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto rounded-2xl border border-border/70 bg-muted/20 p-4">
        <p className="text-sm font-medium">Система оценки v1.0</p>
        <p className="mt-1 text-xs text-muted-foreground">Powered by AI</p>
      </div>
    </aside>
  );
}
