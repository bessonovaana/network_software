# k8s
Kubernetes берёт на себя планирование (scheduler), распределение нагрузки (Service) и самовосстановление (Deployment).
Вы описываете, что и сколько хотите запустить — а кластер сам решает, где и как.
## Ключевые понятия
 - Pod (Под)

    Минимальная единица запуска в Kubernetes.

    Обычно внутри одного Pod’а живёт один контейнер (ваше приложение).

    Pod’ы смертны: если Pod умер, Kubernetes не пытается его «воскресить» — создаётся новый.

    Всё взаимодействие с Pods обычно идёт через Deployment / ReplicaSet.

- Deployment (Развертывание)

    Фабрика Pods.

    Вы говорите: «Хочу 3 копии пода».

    Deployment следит, чтобы их всегда было 3: если один Pod умер, новый будет создан автоматически.

    Deployment также отвечает за безопасные обновления: постепенная замена старых Pod’ов на новые (rolling update).

 - Service (Сервис)

    Единая точка входа для приложения внутри кластера.

    Как внутренний Load Balancer: принимает трафик и раздаёт его по всем живым Pods.

    Для клиентов важно только имя сервиса (например, service1), а не IP конкретного Pod’а.

- Resources (Ресурсы)

    Определяют, сколько ресурсов(eg, память, CPU) нужно и максимально можно использовать Pod’у.

        requests — гарантия от scheduler:
        «Мне нужно минимум 100 МБ памяти, иначе не запускайте меня».

        limits — ограничение:
        «Если я съем больше 500 МБ, прервите меня (OOM Kill)».

    ### Зачем нужны ресурсы?
    Без лимитов один «прожорливый» контейнер может съесть всю память сервера, и ядро Linux начнёт убивать процессы, включая системные.
    Ресурсы — это ограничение, какое право на память и CPU имеет каждый Pod, чтобы соседи не пострадали.

- Probes (Пробы)

    Помогают Kubernetes понять, жив ли Pod и можно ли на него направлять трафик.

        Liveness probe
        «Если я завис и не отвечаю — перезагрузи меня».
        Если probe не проходит, Pod перезапускают.

        Readiness probe
        «Я ещё гружусь, не посылай на меня пользователей».
        Пока readiness не пройдёт успешно, Pod не попадает в список целевых для Service.

## Как запустить пример на кластере Kubernetes (kind)
1. Установка
``` 
# Установка kind (Linux / macOS)
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.25.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Установка kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/kubectl
```
2. Создайте кластер kind
```
kind create cluster --name=network-software
kubectl cluster-info
```
3. Соберите Docker‑образ и загрузите его в kind‑кластер
```
# В корне проекта, где есть docker-compose
docker-compose build 


# Загрузить образ в kind
kind load docker-image network_software-service1:latest
```
4. Применить deployment и service
```
kubectl apply -f k8s
kubectl get pods
```