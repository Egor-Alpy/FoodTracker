# 2.6. Модели в нотации UML

## 2.6.1. Диаграмма вариантов использования (Use Case) — поведенческая

```mermaid
flowchart TB
    subgraph system ["Система FoodTracker"]
        UC1(("Регистрация"))
        UC2(("Авторизация"))
        UC3(("Редактирование профиля"))
        UC4(("Добавление продукта"))
        UC5(("Редактирование продукта"))
        UC6(("Списание продукта"))
        UC7(("Просмотр инвентаря"))
        UC8(("Настройка уведомлений"))
        UC9(("Просмотр статистики"))
        UC10(("Управление списком покупок"))
        UC11(("Создание домохозяйства"))
        UC12(("Приглашение участника"))
        UC13(("Управление участниками"))
        UC14(("Управление справочником"))
        UC15(("Просмотр логов"))
    end

    Guest["Гость"]
    User["Пользователь"]
    Owner["Владелец домохозяйства"]
    Admin["Администратор"]

    Guest --> UC1
    Guest --> UC7

    User --> UC2
    User --> UC3
    User --> UC4
    User --> UC5
    User --> UC6
    User --> UC7
    User --> UC8
    User --> UC9
    User --> UC10
    User --> UC11

    Owner --> UC12
    Owner --> UC13

    Admin --> UC14
    Admin --> UC15

    UC4 -.->|"extend"| UC4a(("Сканирование штрихкода"))
    UC4 -.->|"extend"| UC4b(("Автозаполнение из API"))
    UC6 -.->|"include"| UC6a(("Обновление статистики"))
    UC10 -.->|"extend"| UC10a(("Перенос в инвентарь"))
```

### Комментарии к диаграмме Use Case

**Акторы:**

| Актор | Описание |
|-------|----------|
| Гость | Неавторизованный пользователь. Может просматривать описание сервиса и регистрироваться |
| Пользователь | Авторизованный участник. Полный доступ к функциям учёта продуктов |
| Владелец домохозяйства | Создатель семейной группы. Управляет участниками |
| Администратор | Технический специалист. Управляет справочником и просматривает логи |

**Основные варианты использования:**

- *Регистрация / Авторизация* — создание аккаунта и вход в систему
- *Добавление продукта* — внесение продукта в инвентарь с возможностью сканирования (extend) и автозаполнения (extend)
- *Списание продукта* — отметка об использовании/утилизации, обязательно включает обновление статистики (include)
- *Управление списком покупок* — ведение списка с расширением переноса в инвентарь (extend)
- *Приглашение участника* — добавление членов семьи в домохозяйство

---

## 2.6.2. Диаграмма классов (Class Diagram) — структурная

```mermaid
classDiagram
    class User {
        +int id
        +string email
        +string password_hash
        +string name
        +string avatar_url
        +bool is_verified
        +datetime created_at
        +json notification_settings
        +register()
        +login()
        +updateProfile()
        +updateNotificationSettings()
    }

    class Household {
        +int id
        +string name
        +int owner_id
        +string invite_code
        +datetime created_at
        +create()
        +generateInviteCode()
        +addMember()
        +removeMember()
    }

    class HouseholdMember {
        +int id
        +int household_id
        +int user_id
        +string role
        +datetime joined_at
    }

    class Product {
        +int id
        +int household_id
        +int added_by_id
        +string name
        +string barcode
        +int category_id
        +string storage_location
        +date expiry_date
        +int quantity
        +string unit
        +decimal price
        +string status
        +datetime created_at
        +create()
        +update()
        +consume()
        +discard()
    }

    class Category {
        +int id
        +string name
        +string icon
        +int default_shelf_life_days
    }

    class ProductTemplate {
        +int id
        +string barcode
        +string name
        +int category_id
        +string brand
        +string image_url
        +string source
        +datetime created_at
    }

    class Notification {
        +int id
        +int user_id
        +int product_id
        +string type
        +string title
        +string body
        +bool is_read
        +bool is_sent
        +datetime scheduled_at
        +datetime sent_at
        +send()
        +markAsRead()
    }

    class ShoppingList {
        +int id
        +int household_id
        +string name
        +bool is_active
        +datetime created_at
    }

    class ShoppingItem {
        +int id
        +int list_id
        +string name
        +int quantity
        +string unit
        +bool is_purchased
        +int added_by_id
        +datetime created_at
        +purchase()
        +transferToInventory()
    }

    class ConsumptionLog {
        +int id
        +int product_id
        +int user_id
        +string action
        +datetime created_at
    }

    User "1" --> "*" Household : owns
    User "1" --> "*" HouseholdMember : has
    User "1" --> "*" Product : adds
    User "1" --> "*" Notification : receives
    User "1" --> "*" ShoppingItem : adds
    User "1" --> "*" ConsumptionLog : creates

    Household "1" --> "*" HouseholdMember : contains
    Household "1" --> "*" Product : stores
    Household "1" --> "*" ShoppingList : has

    HouseholdMember "*" --> "1" User : references

    Product "*" --> "1" Category : belongs_to
    Product "1" --> "*" Notification : triggers
    Product "1" --> "*" ConsumptionLog : has

    ProductTemplate "*" --> "1" Category : belongs_to

    ShoppingList "1" --> "*" ShoppingItem : contains
```

### Комментарии к диаграмме классов

**Основные сущности:**

| Класс | Описание |
|-------|----------|
| User | Пользователь системы. Хранит учётные данные и настройки уведомлений |
| Household | Домохозяйство. Объединяет пользователей для совместного доступа |
| HouseholdMember | Связь пользователя с домохозяйством. Роли: owner / member |
| Product | Продукт в инвентаре. Основная сущность с информацией о сроке годности |
| Category | Категория продуктов. Справочник с иконками и сроками хранения по умолчанию |
| ProductTemplate | Шаблон продукта из справочника. Данные из API или ранее добавленных |
| Notification | Уведомление. Привязано к пользователю и продукту |
| ShoppingList | Список покупок. Принадлежит домохозяйству |
| ShoppingItem | Позиция в списке покупок |
| ConsumptionLog | Лог потребления. Фиксирует использование/утилизацию для статистики |

**Ключевые связи:**

- User → Household: пользователь может владеть несколькими домохозяйствами (1:*)
- Household → Product: домохозяйство содержит много продуктов (1:*)
- Product → Notification: один продукт может иметь несколько уведомлений (1:*)
- Product → ConsumptionLog: история действий с продуктом (1:*)

**Статусы Product:**
- `active` — продукт в наличии
- `expiring_soon` — срок истекает в ближайшие дни
- `expired` — срок истёк
- `consumed` — использован
- `discarded` — выброшен

---

## 2.6.3. Диаграмма последовательности (Sequence Diagram) — поведенческая

### Сценарий: Добавление продукта сканированием штрихкода

```mermaid
sequenceDiagram
    autonumber
    participant U as Пользователь
    participant App as Приложение
    participant API as Backend API
    participant CZ as Честный знак
    participant OFF as Open Food Facts
    participant DB as База данных

    U->>App: Открыть сканер
    App->>App: Активировать камеру
    U->>App: Навести на штрихкод
    App->>App: Декодировать штрихкод
    App->>API: POST /products/lookup {barcode}
    
    API->>CZ: GET /product/{datamatrix}
    
    alt Товар найден в Честном знаке
        CZ-->>API: {name, brand, expiry_date}
        API-->>App: {found: true, source: "chestnyznak", data: {...}}
    else Товар не найден
        CZ-->>API: 404 Not Found
        API->>OFF: GET /product/{barcode}
        
        alt Товар найден в Open Food Facts
            OFF-->>API: {name, brand, category, image}
            API-->>App: {found: true, source: "openfoodfacts", data: {...}}
        else Товар не найден
            OFF-->>API: 404 Not Found
            API->>DB: SELECT * FROM product_templates WHERE barcode = ?
            
            alt Товар найден в локальной базе
                DB-->>API: {name, category}
                API-->>App: {found: true, source: "local", data: {...}}
            else Товар не найден
                DB-->>API: null
                API-->>App: {found: false}
            end
        end
    end

    App->>U: Показать форму с данными
    U->>App: Указать срок годности
    U->>App: Выбрать место хранения
    U->>App: Сохранить
    
    App->>API: POST /products {name, barcode, expiry_date, ...}
    API->>DB: INSERT INTO products
    API->>DB: INSERT INTO product_templates (if new)
    API->>API: Рассчитать дату уведомления
    API->>DB: INSERT INTO notifications (scheduled)
    API-->>App: {success: true, product_id}
    App->>U: Продукт добавлен
```

### Сценарий: Автоматическая отправка уведомлений

```mermaid
sequenceDiagram
    autonumber
    participant Cron as Планировщик
    participant Worker as Celery Worker
    participant DB as База данных
    participant FCM as Firebase Cloud Messaging
    participant Email as Email Service
    participant U as Пользователь

    Cron->>Worker: Запуск задачи check_expiring_products
    Worker->>DB: SELECT products WHERE expiry_date - today <= notify_days
    DB-->>Worker: Список истекающих продуктов
    
    loop Для каждого продукта
        Worker->>DB: SELECT user settings WHERE household_id = ?
        DB-->>Worker: Настройки пользователей
        
        Worker->>Worker: Сформировать текст уведомления
        
        alt Push-уведомления включены
            Worker->>FCM: POST /send {token, title, body}
            FCM-->>Worker: {success: true}
            FCM->>U: Push-уведомление
        end
        
        alt Email-уведомления включены
            Worker->>Email: POST /send {to, subject, body}
            Email-->>Worker: {success: true}
            Email->>U: Email
        end
        
        Worker->>DB: UPDATE notifications SET is_sent = true
    end
    
    Worker->>Cron: Задача завершена
```

### Комментарии к диаграммам последовательности

**Сценарий «Добавление продукта»:**

1. **Сканирование (шаги 1–4):** Пользователь открывает сканер, приложение активирует камеру и декодирует штрихкод.

2. **Каскадный поиск (шаги 5–16):** 
   - Приоритет: Честный знак (возвращает срок годности для маркированных товаров)
   - Fallback: Open Food Facts (название, категория, изображение)
   - Финальный fallback: локальная база ранее добавленных товаров

3. **Заполнение формы (шаги 17–20):** Автозаполненные данные показываются пользователю, он дополняет срок годности и место хранения.

4. **Сохранение (шаги 21–26):** Продукт записывается в БД, новый товар добавляется в справочник, планируется уведомление.

**Сценарий «Отправка уведомлений»:**

1. **Запуск (шаги 1–3):** Планировщик (Celery Beat) запускает задачу по расписанию (например, каждый час).

2. **Выборка (шаги 2–3):** Запрос продуктов, у которых срок годности наступает в пределах настроек пользователя.

3. **Обработка (цикл):** Для каждого продукта:
   - Получение настроек пользователей домохозяйства
   - Формирование персонализированного текста
   - Отправка через выбранные каналы (Push и/или Email)
   - Отметка уведомления как отправленного

---

## 2.6.4. Диаграмма деятельности (Activity Diagram) — поведенческая

```mermaid
flowchart TB
    subgraph swimlane1 ["Пользователь"]
        A1(("●"))
        A2["Открыть приложение"]
        A3{"Авторизован?"}
        A4["Войти в систему"]
        A5["Просмотреть инвентарь"]
        A6{"Есть истекающие<br/>продукты?"}
        A7["Выбрать действие"]
        A8["Использовать продукт"]
        A9["Выбросить продукт"]
        A10{"Добавить в<br/>список покупок?"}
        A11["Подтвердить"]
        A12(("◉"))
    end
    
    subgraph swimlane2 ["Система"]
        B1["Проверить сессию"]
        B2["Загрузить инвентарь"]
        B3["Выделить истекающие"]
        B4["Обновить статус"]
        B5["Записать в историю"]
        B6["Обновить статистику"]
        B7["Добавить в список"]
    end
    
    A1 --> A2 --> B1 --> A3
    A3 -->|"Нет"| A4 --> B1
    A3 -->|"Да"| B2 --> B3 --> A5 --> A6
    A6 -->|"Нет"| A12
    A6 -->|"Да"| A7
    A7 --> A8 --> B4
    A7 --> A9 --> B4
    B4 --> B5 --> B6 --> A10
    A10 -->|"Да"| A11 --> B7 --> A12
    A10 -->|"Нет"| A12
```

### Комментарии к диаграмме деятельности

**Дорожки (swimlanes):**
- Пользователь — действия, инициируемые человеком
- Система — автоматические операции

**Основной сценарий:**
1. Пользователь открывает приложение
2. Система проверяет авторизацию
3. Загружается инвентарь с выделением истекающих продуктов
4. Пользователь выбирает действие: использовать или выбросить
5. Система обновляет статус, записывает в историю, обновляет статистику
6. Предложение добавить в список покупок

**Точки принятия решений:**
- Авторизован? — переход к входу или к инвентарю
- Есть истекающие? — продолжение работы или завершение
- Добавить в список? — интеграция со списком покупок
