# backend/create_superuser.py
import os
import sys
import django

# Proje dizinini Python path'e ekle
sys.path.insert(0, '/app/backend/backend')

# Çalışma dizinini değiştir
os.chdir('/app/backend/backend')

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# .env dosyasından kullanıcı adı ve şifreyi al
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin')

# Eğer kullanıcı zaten mevcut değilse oluştur
if not User.objects.filter(username=username).exists():
    print(f"Süper kullanıcı '{username}' oluşturuluyor...")
    User.objects.create_superuser(username=username, email='admin@example.com', password=password)
    print("Süper kullanıcı başarıyla oluşturuldu.")
else:
    print(f"Süper kullanıcı '{username}' zaten mevcut, atlanıyor.")