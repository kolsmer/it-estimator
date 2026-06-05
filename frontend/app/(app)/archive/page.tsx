"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Archive } from 'lucide-react';
import { EmptyState } from '@/components/layout/empty-state';
import { PageHeader } from '@/components/layout/page-header';
import { ProjectActions } from '@/components/layout/project-actions';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { BackendProject, getBackendUrl } from '@/lib/backend';

export default function ArchivePage() {
  const [projects, setProjects] = useState<BackendProject[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadProjects() {
      const backendUrl = getBackendUrl();
      if (!backendUrl) {
        setError('Не задан NEXT_PUBLIC_BACKEND_URL');
        setLoading(false);
        return;
      }

      try {
        const response = await fetch(`${backendUrl}/projects/archived`, { cache: 'no-store' });
        if (!response.ok) {
          throw new Error('Не удалось загрузить архив');
        }
        const data = (await response.json()) as BackendProject[];
        setProjects(Array.isArray(data) ? data : []);
      } catch {
        setError('Backend не отвечает или архив недоступен');
      } finally {
        setLoading(false);
      }
    }

    loadProjects();
  }, []);

  return (
    <div>
      <PageHeader title="Архив" subtitle="Архивные проекты" actionLabel="К проектам" actionHref="/projects" />

      <Card>
        <CardHeader>
          <CardTitle>Архивные проекты</CardTitle>
          <CardDescription>Восстановление и удаление архивных проектов.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {loading ? (
            <p className="text-sm text-muted-foreground">Загрузка архива...</p>
          ) : error ? (
            <EmptyState icon={Archive} title="Архив недоступен" description={error} />
          ) : projects.length ? (
            projects.map((project) => (
              <div key={project.id} className="rounded-2xl border border-border/70 bg-muted/20 p-4">
                <div className="mb-3">
                  <Link href={`/projects/${project.id}`} className="font-medium hover:underline">
                    {project.name}
                  </Link>
                  <p className="text-sm text-muted-foreground">
                    {project.client} · {Number(project.cost).toLocaleString('ru-RU')} ₽
                  </p>
                </div>
                <ProjectActions
                  projectId={project.id}
                  projectName={project.name}
                  initialStatus="archived"
                  onDeleted={() => setProjects((prev) => prev.filter((item) => item.id !== project.id))}
                  onStatusChange={(status) => {
                    if (status === 'active') {
                      setProjects((prev) => prev.filter((item) => item.id !== project.id));
                    }
                  }}
                />
              </div>
            ))
          ) : (
            <EmptyState icon={Archive} title="Архив пуст" description="В архиве пока нет проектов." />
          )}
        </CardContent>
      </Card>
    </div>
  );
}

