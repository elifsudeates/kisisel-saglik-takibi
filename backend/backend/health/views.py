from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from influxdb_client import InfluxDBClient
import json
from .forms import DailyEntryForm
from .models import DailyEntry
from django.utils import timezone
from django.contrib import messages
from datetime import datetime


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def dashboard(request):
    # InfluxDB bağlantısı
    try:
        influx_client = InfluxDBClient(
            url=settings.INFLUXDB_URL,
            token=settings.INFLUXDB_TOKEN,
            org=settings.INFLUXDB_ORG
        )
        query_api = influx_client.query_api()

        # Influx verisini çek
        query = f'''
        from(bucket: "{settings.INFLUXDB_BUCKET}")
          |> range(start: -12h)
          |> filter(fn: (r) => r["_measurement"] == "saglik_verisi")
          |> filter(fn: (r) => r["user_id"] == "{request.user.username}")
          |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
          |> sort(columns: ["_time"], desc: false)
        '''
        result = query_api.query_data_frame(query)

    except Exception as e:
        messages.error(request, f"Sağlık verileri sunucusuna bağlanılamadı: {e}")
        result = None # Hata durumunda result'ı None yap

    records = []
    if result is not None and not result.empty:
        result = result.rename(columns={'_time': 'time'})
        for _, row in result.iterrows():
            records.append({
                'time': row['time'].strftime('%Y-%m-%d %H:%M'),
                'nabiz': row.get('nabiz'),
                'oksijen': row.get('oksijen'),
                'seker': row.get('seker'),
                'sistolik': row.get('tansiyon_sistolik'),
                'diastolik': row.get('tansiyon_diastolik')
            })

    # Günlük form işleme
    today = timezone.now().date()
    entry, _ = DailyEntry.objects.get_or_create(user=request.user, date=today)

    if request.method == 'POST':
        form = DailyEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            messages.success(request, "Günlük bilgiler kaydedildi.")
            return redirect('dashboard')
    else:
        form = DailyEntryForm(instance=entry)

    # Uyarılar
    alerts = []

    # Su ve uyku uyarıları
    if entry.water_liters is not None and entry.water_liters < 3.0:
        alerts.append(f"Bugünkü su tüketimi düşük: {entry.water_liters} L (≥ 3 L önerilir)")

    if entry.sleep_hours is not None:
      if entry.sleep_hours < 6.0:
          alerts.append(f"Bugünkü uyku süresi çok az: {entry.sleep_hours} saat")
      elif entry.sleep_hours > 9.0:
          alerts.append(f"Bugünkü uyku süresi fazla: {entry.sleep_hours} saat")

    # Sensör verisine göre uyarılar
    if records:
        latest = records[-1]
        if latest.get('nabiz') and (latest['nabiz'] < 60 or latest['nabiz'] > 100):
            alerts.append(f"Nabız değeri anormal: {latest['nabiz']} bpm")
        if latest.get('oksijen') and latest['oksijen'] < 95:
            alerts.append(f"Oksijen seviyesi düşük: %{latest['oksijen']}")
        if latest.get('seker') and (latest['seker'] < 70 or latest['seker'] > 140):
            alerts.append(f"Kan şekeri değeri anormal: {latest['seker']} mg/dL")
        if latest.get('sistolik') and latest.get('diastolik') and (latest['sistolik'] > 140 or latest['diastolik'] > 90):
            alerts.append(f"Tansiyon yüksek: {latest['sistolik']}/{latest['diastolik']} mmHg")

    # Grafik verilerini hazırla
    tansiyon_chart_data = {
        'labels': [r['time'] for r in records],
        'sistolik': [r.get('sistolik') for r in records],
        'diastolik': [r.get('diastolik') for r in records],
    }

    history = DailyEntry.objects.filter(user=request.user).order_by('date')
    sleep_chart = [(e.date.strftime('%Y-%m-%d'), e.sleep_hours or 0.0) for e in history]
    water_chart = [(e.date.strftime('%Y-%m-%d'), e.water_liters or 0.0) for e in history]

    context = {
        'user': request.user,
        'form': form,
        'alerts': alerts,
        'records_json': json.dumps(records),
        'sleep_chart': json.dumps(sleep_chart),
        'water_chart': json.dumps(water_chart),
        'tansiyon_chart_data': json.dumps(tansiyon_chart_data),
    }

    return render(request, 'dashboard.html', context)