"use client";

import Link from 'next/link';
import { useCallback, useEffect, useState } from 'react';
import { PageHeader } from '@/components/layout/page-header';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { getBackendUrl } from '@/lib/backend';

type RoleRate = {
  id: string;
  role: string;
  rate: number;
  currency: string;
  role_key: string;
  seniority: string;
};

export default function RolesPage() {
  const [roleRates, setRoleRates] = useState<RoleRate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const backendUrl = getBackendUrl();

  const loadRoleRates = useCallback(async () => {
    if (!backendUrl) {
      setError('Не задан NEXT_PUBLIC_BACKEND_URL');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${backendUrl}/roles`, { cache: 'no-store' });
      if (!response.ok) {
        throw new Error('Не удалось загрузить роли');
      }
      const data = (await response.json()) as RoleRate[];
      setRoleRates(Array.isArray(data) ? data : []);
      setError('');
    } catch {
      setError('Backend не отвечает или роли недоступны');
    } finally {
      setLoading(false);
    }
  }, [backendUrl]);

  useEffect(() => {
    loadRoleRates();
  }, [loadRoleRates]);

  async function updateRate(rate: RoleRate) {
    if (!backendUrl) {
      alert('Не задан NEXT_PUBLIC_BACKEND_URL');
      return;
    }

    const rawValue = window.prompt(`Новая ставка для ${rate.role}:`, String(rate.rate));
    if (!rawValue) return;

    const nextRate = Number(rawValue.replace(',', '.'));
    if (!Number.isFinite(nextRate) || nextRate <= 0) {
      alert('Ставка должна быть положительным числом');
      return;
    }

    try {
      const response = await fetch(`${backendUrl}/settings/rates`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          role: rate.role_key,
          seniority: rate.seniority,
          rate: nextRate,
        }),
      });
      const payload = await response.json().catch(() => ({}));

      if (!response.ok || payload.success === false) {
        throw new Error(payload.detail || payload.error || 'Не удалось обновить ставку');
      }

      await loadRoleRates();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Не удалось обновить ставку');
    }
  }

  return (
    <div>
      <PageHeader
        title="Роли и ставки"
        subtitle="Настройка команды проекта"
        actionLabel="К проектам"
        actionHref="/projects"
      />

      <Card>
        <CardHeader>
          <CardTitle>Роли</CardTitle>
          <CardDescription>Ставки загружаются и обновляются через backend API.</CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          {loading ? (
            <p className="text-sm text-muted-foreground">Загрузка ролей...</p>
          ) : error ? (
            <p className="text-sm text-muted-foreground">{error}</p>
          ) : roleRates.length ? (
            <div className="space-y-2">
              {roleRates.map((rate) => (
                <div key={rate.id} className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-border/70 bg-muted/20 p-4">
                  <div>
                    <p className="font-medium">{rate.role}</p>
                    <p className="text-sm text-muted-foreground">
                      {rate.rate.toLocaleString('ru-RU')} {rate.currency}
                    </p>
                  </div>
                  <Button variant="outline" onClick={() => updateRate(rate)}>
                    Изменить
                  </Button>
                </div>
              ))}
            </div>
          ) : (
            <p>Пока ролей нет.</p>
          )}

          <Link href="/projects">
            <Button>Перейти к проектам</Button>
          </Link>
        </CardContent>
      </Card>
    </div>
  );
}
