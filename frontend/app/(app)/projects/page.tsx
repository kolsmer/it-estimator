"use client";

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { FolderOpen } from 'lucide-react';
import { EmptyState } from '@/components/layout/empty-state';
import { PageHeader } from '@/components/layout/page-header';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { BackendProject, getBackendUrl } from '@/lib/backend';

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

export default function ProjectsPage() {
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
        const response = await fetch(`${backendUrl}/projects`, { cache: 'no-store' });

        if (!response.ok) {
          throw new Error('Не удалось загрузить список проектов');
        }

        const data = (await response.json()) as BackendProject[];
        setProjects(Array.isArray(data) ? data : []);
      } catch {
        setError('Backend не отвечает или список проектов недоступен');
      } finally {
        setLoading(false);
      }
    }

    loadProjects();
  }, []);

  return (
    <div>
      <PageHeader
        title="Проекты"
        subtitle="Список проектов из backend API"
        actionLabel="Новый проект"
      />

      <Card>
        <CardHeader>
          <CardTitle>Проекты</CardTitle>
          <CardDescription>Данные загружаются из FastAPI.</CardDescription>
        </CardHeader>

        <CardContent>
          {loading ? (
            <p className="text-sm text-muted-foreground">Загрузка проектов...</p>
          ) : error ? (
            <EmptyState icon={FolderOpen} title="Нет проектов" description={error} />
          ) : projects.length ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Название</TableHead>
                  <TableHead>Тип</TableHead>
                  <TableHead>Статус</TableHead>
                  <TableHead className="text-right">Недели</TableHead>
                  <TableHead className="text-right">Стоимость</TableHead>
                </TableRow>
              </TableHeader>

              <TableBody>
                {projects.map((project) => (
                  <TableRow key={project.id}>
                    <TableCell className="font-medium">
                      <Link href={`/projects/${project.id}`} className="hover:underline">
                        {project.name}
                      </Link>
                    </TableCell>
                    <TableCell>{projectTypeLabel(project.project_type || project.client)}</TableCell>
                    <TableCell>{project.status}</TableCell>
                    <TableCell className="text-right">{project.hours}</TableCell>
                    <TableCell className="text-right">
                      {Number(project.cost).toLocaleString('ru-RU')} ₽
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <EmptyState
              icon={FolderOpen}
              title="Нет проектов"
              description="База пустая."
            />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
