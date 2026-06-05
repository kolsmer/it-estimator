import Link from 'next/link';
import { FolderKanban, Layers3, ReceiptText, Timer } from 'lucide-react';
import { PageHeader } from '@/components/layout/page-header';
import { EmptyState } from '@/components/layout/empty-state';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { fetchProjects } from '@/lib/backend-server';

export default async function DashboardPage() {
  const projects = await fetchProjects();

  const totalHours = projects.reduce((acc, project) => acc + Number(project.hours || 0), 0);
  const totalCostValue = projects.reduce((acc, project) => acc + Number(project.cost || 0), 0);
  const totalCost = `${totalCostValue.toLocaleString('ru-RU')} ₽`;

  const kpis = [
    {
      title: 'Всего проектов',
      value: String(projects.length),
      icon: FolderKanban,
      gradient: 'from-violet-600/30 via-violet-500/10 to-transparent',
    },
    {
      title: 'Активных',
      value: String(projects.filter((item) => item.status === 'active').length),
      icon: Layers3,
      gradient: 'from-cyan-500/30 via-emerald-500/10 to-transparent',
    },
    {
      title: 'Всего недель',
      value: String(totalHours),
      icon: Timer,
      gradient: 'from-emerald-500/30 via-lime-500/10 to-transparent',
    },
    {
      title: 'Общая стоимость',
      value: totalCost,
      icon: ReceiptText,
      gradient: 'from-orange-500/30 via-amber-500/10 to-transparent',
    },
  ];

  return (
    <div>
      <PageHeader
        title="Дашборд"
        subtitle="Обзор оценок ИТ-проектов"
        actionLabel="К проектам"
        actionHref="/projects"
      />

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {kpis.map((item) => {
          const Icon = item.icon;

          return (
            <Card key={item.title} className="relative overflow-hidden border-border/70">
              <div className={`absolute inset-0 bg-gradient-to-br ${item.gradient}`} />
              <CardHeader className="relative flex-row items-start justify-between space-y-0">
                <CardDescription>{item.title}</CardDescription>
                <div className="rounded-xl bg-slate-900/70 p-2 text-muted-foreground">
                  <Icon className="h-4 w-4" />
                </div>
              </CardHeader>
              <CardContent className="relative">
                <p className="text-3xl font-semibold tracking-tight">{item.value}</p>
              </CardContent>
            </Card>
          );
        })}
      </section>

      <section className="mt-6 grid gap-6 xl:grid-cols-3">
        <Card className="xl:col-span-2">
          <CardHeader>
            <CardTitle>Недавние проекты</CardTitle>
            <CardDescription>Последние изменения по оценкам и статусам проектов.</CardDescription>
          </CardHeader>

          <CardContent>
            {projects.length ? (
              <div className="space-y-3">
                {projects.slice(0, 5).map((project) => (
                  <Link
                    key={project.id}
                    href={`/projects/${project.id}`}
                    className="block rounded-2xl border border-border/70 bg-muted/20 p-4 transition hover:bg-muted/40"
                  >
                    <p className="font-medium">{project.name}</p>
                    <p className="mt-1 text-sm text-muted-foreground">
                      {project.client} · {Number(project.cost).toLocaleString('ru-RU')} ₽
                    </p>
                  </Link>
                ))}
              </div>
            ) : (
              <EmptyState
                icon={FolderKanban}
                title="Нет проектов"
                description="Создайте первый проект, чтобы заполнить дашборд."
              />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Быстрые действия</CardTitle>
            <CardDescription>Основные переходы по системе.</CardDescription>
          </CardHeader>

          <CardContent className="grid gap-3">
            <Link
              href="/projects"
              className="rounded-2xl border border-border/70 bg-muted/20 p-4 text-left transition hover:bg-muted/40"
            >
              <p className="font-medium">Проекты</p>
              <p className="text-sm text-muted-foreground">Посмотреть список проектов из базы.</p>
            </Link>

            <Link
              href="/roles"
              className="rounded-2xl border border-border/70 bg-muted/20 p-4 text-left transition hover:bg-muted/40"
            >
              <p className="font-medium">Роли и ставки</p>
              <p className="text-sm text-muted-foreground">Открыть страницу ролей.</p>
            </Link>
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
