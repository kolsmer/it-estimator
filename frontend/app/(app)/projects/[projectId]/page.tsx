"use client";

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Clock3, DollarSign, Download, ShieldCheck, Sparkles, Users2 } from 'lucide-react';
import { ProjectActions } from '@/components/layout/project-actions';
import { EmptyState } from '@/components/layout/empty-state';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { BackendProject, getBackendUrl } from '@/lib/backend';

type ProjectDetailsPageProps = {
  params: {
    projectId: string;
  };
};

function statusLabel(status: string) {
  if (status === 'active') return 'Активный';
  if (status === 'archived') return 'В архиве';
  if (status === 'paused') return 'На паузе';
  if (status === 'done') return 'Завершён';
  return status;
}

function projectTypeLabel(value?: string) {
  const labels: Record<string, string> = {
    website: 'Веб-сайт',
    web_app: 'Веб-приложение',
    mobile_app: 'Мобильное приложение',
    ecommerce: 'Интернет-магазин',
    marketplace: 'Маркетплейс',
    crm: 'CRM-система',
    erp: 'ERP-система',
    api: 'Backend API',
    chatbot: 'Чат-бот',
    ai_service: 'AI-сервис',
    other: 'Другой проект',
  };
  return labels[value || ''] || value || '—';
}

const exportFormats = ['json', 'csv', 'xlsx', 'xls'];

type ParsedInputProject = {
  description?: string;
  features?: Array<{ name?: string; complexity?: string }>;
  design_complexity?: string;
  backend_complexity?: string;
  frontend_complexity?: string;
  target_platforms?: string[];
  integrations?: string[];
};

type ParsedEstimate = {
  total_hours?: number;
  hourly_rate_avg_rub?: number;
  confidence_score?: number;
};

function parseJsonField<T>(value?: string): T | null {
  if (!value) return null;
  try {
    return JSON.parse(value) as T;
  } catch {
    return null;
  }
}

function formatDate(value?: string) {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function complexityLabel(value?: string) {
  if (value === 'low') return 'Низкая';
  if (value === 'medium') return 'Средняя';
  if (value === 'high') return 'Высокая';
  if (value === 'critical') return 'Критичная';
  return value || '—';
}

function renderLlmAnalysis(text: string) {
  const lines = text
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean);

  return lines.map((line, index) => {
    const normalized = line.replace(/^[-•]\s*/, '').replace(/^\d+\.\s*/, '');
    const headingMatch = normalized.match(/^(Суть(?: проекта)?|Риски|Рекомендации|Итог|Оценка сроков):?$/i);

    if (headingMatch) {
      const heading = headingMatch[1].toLowerCase() === 'суть проекта' ? 'Суть' : headingMatch[1];
      return (
        <h4 key={`${line}-${index}`} className={index === 0 ? 'text-sm font-semibold text-foreground' : 'pt-3 text-sm font-semibold text-foreground'}>
          {heading}
        </h4>
      );
    }

    return (
      <div key={`${line}-${index}`} className="flex gap-3 rounded-xl bg-background/70 px-3 py-2">
        <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-foreground/50" />
        <p className="text-sm leading-6 text-muted-foreground">{normalized}</p>
      </div>
    );
  });
}

export default function ProjectDetailsPage({ params }: ProjectDetailsPageProps) {
  const router = useRouter();
  const [project, setProject] = useState<BackendProject | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const backendUrl = getBackendUrl();

  useEffect(() => {
    async function loadProject() {
      if (!backendUrl) {
        setError('Не задан NEXT_PUBLIC_BACKEND_URL');
        setLoading(false);
        return;
      }

      try {
        const response = await fetch(`${backendUrl}/projects/${params.projectId}`, { cache: 'no-store' });

        if (!response.ok) {
          throw new Error('Проект не найден');
        }

        const data = (await response.json()) as BackendProject;
        setProject(data);
      } catch {
        setError('Backend не отвечает или проект недоступен');
      } finally {
        setLoading(false);
      }
    }

    loadProject();
  }, [backendUrl, params.projectId]);

  if (loading) {
    return <p className="text-sm text-muted-foreground">Загрузка проекта...</p>;
  }

  if (error || !project) {
    return <EmptyState icon={Users2} title="Проект не найден" description={error || 'Нет данных по проекту'} />;
  }

  const inputProject = parseJsonField<ParsedInputProject>(project.input_project);
  const estimate = parseJsonField<ParsedEstimate>(project.estimation);
  const featureList = inputProject?.features?.filter((feature) => feature.name) ?? [];
  const platforms = inputProject?.target_platforms?.length ? inputProject.target_platforms : [];
  const integrations = inputProject?.integrations?.length ? inputProject.integrations : [];

  return (
    <div>
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div className="space-y-2">
          <Link href="/projects" className="inline-flex items-center gap-2 text-sm text-muted-foreground transition hover:text-foreground">
            <ArrowLeft className="h-4 w-4" />
            Назад к проектам
          </Link>
          <div>
            <h2 className="text-3xl font-semibold">{project.name}</h2>
            <p className="text-sm text-muted-foreground">Карточка проекта и сценарии управления</p>
          </div>
        </div>

        <div className="rounded-2xl border border-border/70 bg-muted/20 px-4 py-3 text-sm text-muted-foreground">
          Статус: <span className="font-medium text-foreground">{statusLabel(project.status)}</span>
        </div>
      </div>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Card>
          <CardHeader className="flex-row items-start justify-between space-y-0">
            <CardDescription>Тип проекта</CardDescription>
            <Users2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-semibold tracking-tight">{projectTypeLabel(project.project_type || project.client)}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex-row items-start justify-between space-y-0">
            <CardDescription>Недели</CardDescription>
            <Clock3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-semibold tracking-tight">{project.hours}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex-row items-start justify-between space-y-0">
            <CardDescription>Стоимость</CardDescription>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-semibold tracking-tight">{Number(project.cost).toLocaleString('ru-RU')} ₽</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex-row items-start justify-between space-y-0">
            <CardDescription>Команда</CardDescription>
            <ShieldCheck className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-semibold tracking-tight">{project.team_size}</p>
          </CardContent>
        </Card>
      </section>

      <section className="mt-6 grid gap-6 xl:grid-cols-3">
        <Card className="xl:col-span-3">
          <CardHeader className="flex-row items-start justify-between space-y-0">
            <div>
              <CardTitle>LLM-анализ</CardTitle>
              <CardDescription>Пояснение, риски и рекомендации, которые backend получил от Ollama.</CardDescription>
            </div>
            <Sparkles className="h-5 w-5 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {project.llm_analysis ? (
              <div className="space-y-2 rounded-2xl border border-border/70 bg-muted/20 p-4">
                {renderLlmAnalysis(project.llm_analysis)}
              </div>
            ) : (
              <p className="rounded-2xl border border-border/70 bg-muted/20 p-4 text-sm text-muted-foreground">
                LLM-анализ для этого проекта отсутствует.
              </p>
            )}
          </CardContent>
        </Card>

        <Card className="xl:col-span-2">
          <CardHeader>
            <CardTitle>Требования и расчёт</CardTitle>
            <CardDescription>Исходные данные, которые backend использовал для оценки.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-2xl border border-border/70 bg-muted/20 p-4">
                <p className="text-sm text-muted-foreground">ID</p>
                <p className="mt-1 font-medium">{project.id}</p>
              </div>
              <div className="rounded-2xl border border-border/70 bg-muted/20 p-4">
                <p className="text-sm text-muted-foreground">Дата расчёта</p>
                <p className="mt-1 font-medium">{formatDate(project.generated_at)}</p>
              </div>
              <div className="rounded-2xl border border-border/70 bg-muted/20 p-4">
                <p className="text-sm text-muted-foreground">Тип проекта</p>
                <p className="mt-1 font-medium">{projectTypeLabel(project.project_type || project.client)}</p>
              </div>
              <div className="rounded-2xl border border-border/70 bg-muted/20 p-4">
                <p className="text-sm text-muted-foreground">Всего часов</p>
                <p className="mt-1 font-medium">{estimate?.total_hours ?? '—'}</p>
              </div>
              <div className="rounded-2xl border border-border/70 bg-muted/20 p-4">
                <p className="text-sm text-muted-foreground">Средняя ставка</p>
                <p className="mt-1 font-medium">
                  {estimate?.hourly_rate_avg_rub ? `${Number(estimate.hourly_rate_avg_rub).toLocaleString('ru-RU')} ₽/ч` : '—'}
                </p>
              </div>
              <div className="rounded-2xl border border-border/70 bg-muted/20 p-4">
                <p className="text-sm text-muted-foreground">Качество входных данных</p>
                <p className="mt-1 font-medium">{estimate?.confidence_score ? `${Math.round(estimate.confidence_score * 100)}%` : '—'}</p>
                <p className="mt-1 text-xs leading-5 text-muted-foreground">
                  Внутренняя эвристика: выше, если есть срок, бюджет или похожие проекты.
                </p>
              </div>
            </div>

            <div className="rounded-2xl border border-border/70 bg-muted/20 p-4">
              <p className="text-sm text-muted-foreground">Описание</p>
              <p className="mt-2 text-sm leading-6">{inputProject?.description || 'Описание не сохранено'}</p>
            </div>

            <div className="rounded-2xl border border-border/70 bg-muted/20 p-4">
              <p className="text-sm text-muted-foreground">Функции</p>
              {featureList.length ? (
                <div className="mt-3 flex flex-wrap gap-2">
                  {featureList.map((feature, index) => (
                    <span key={`${feature.name}-${index}`} className="rounded-full border border-border bg-background px-3 py-1 text-xs">
                      {feature.name} · {complexityLabel(feature.complexity)}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="mt-2 text-sm text-muted-foreground">Функции не выделены</p>
              )}
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-2xl border border-border/70 bg-muted/20 p-4">
                <p className="text-sm text-muted-foreground">Сложность</p>
                <p className="mt-2 text-sm leading-6">
                  Дизайн: {complexityLabel(inputProject?.design_complexity)}
                  <br />
                  Backend: {complexityLabel(inputProject?.backend_complexity)}
                  <br />
                  Frontend: {complexityLabel(inputProject?.frontend_complexity)}
                </p>
              </div>
              <div className="rounded-2xl border border-border/70 bg-muted/20 p-4">
                <p className="text-sm text-muted-foreground">Платформы и интеграции</p>
                <p className="mt-2 text-sm leading-6">
                  Платформы: {platforms.length ? platforms.join(', ') : '—'}
                  <br />
                  Интеграции: {integrations.length ? integrations.join(', ') : '—'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Архив / удаление</CardTitle>
            </CardHeader>
            <CardContent>
              <ProjectActions
                projectId={project.id}
                projectName={project.name}
                initialStatus={project.status}
                onDeleted={() => router.push('/projects')}
                onStatusChange={(nextStatus) => setProject({ ...project, status: nextStatus })}
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Экспорт</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-3">
              {exportFormats.map((format) => (
                <a
                  key={format}
                  href={`${backendUrl}/projects/${project.id}/export?format=${format}`}
                  className="inline-flex h-10 items-center justify-center gap-2 rounded-2xl border border-border bg-card px-4 py-2 text-sm font-medium transition-colors hover:bg-muted"
                >
                  <Download className="h-4 w-4" />
                  {format.toUpperCase()}
                </a>
              ))}
            </CardContent>
          </Card>
        </div>
      </section>
    </div>
  );
}
