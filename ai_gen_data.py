import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import random
from google.oauth2 import service_account
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

np.random.seed(42)
random.seed(42)


# Customer Profile (Platzhalter für Chats und Support-Anfragen)


n_customers = 1000

customer_profile = pd.DataFrame({
    'customer_id': [f'CUST_{i:05d}' for i in range(1, n_customers + 1)],
    'signup_date': pd.date_range(end='2026-01-01', periods=n_customers, freq='2D'),
    'plan_tier': np.random.choice(['Basic_50Mbps', 'Standard_200Mbps', 'Premium_1Gbps'], 
                                  n_customers, p=[0.35, 0.45, 0.2]),
    'address': "",
    'contract_type': np.random.choice(['monthly', 'annual', '2-year'], 
                                     n_customers, p=[0.5, 0.3, 0.2]),
    'autopay_enabled': np.random.choice([True, False], n_customers, p=[0.7, 0.3])
})

print("Customer Profile created")


# Churn Rate


churn_rate = 0.15
n_churned = int(n_customers * churn_rate)
churned_customers = np.random.choice(customer_profile['customer_id'], n_churned, replace=False)

churn_labels = pd.DataFrame({
    'customer_id': customer_profile['customer_id'],
    'churned': customer_profile['customer_id'].isin(churned_customers).astype(int)
})

churn_labels['churn_date'] = None
churn_labels.loc[churn_labels['churned'] == 1, 'churn_date'] = [
    datetime(2026, 3, 1) - timedelta(days=random.randint(1, 90)) 
    for _ in range(n_churned)
]

churn_reasons = ['competitor_price', 'poor_service', 'technical_issues', 'relocation', 'price_increase', 'unknown']
churn_labels.loc[churn_labels['churned'] == 1, 'churn_reason'] = np.random.choice(
    churn_reasons, n_churned, p=[0.35, 0.20, 0.20, 0.10, 0.05, 0.1]
)

print("Churn Labels erstellt")


# Connection Logs


connection_logs = []
log_id = 1

# Dictionary um technische Probleme pro Kunde zu tracken
customer_technical_issues = {}

for customer_id in customer_profile['customer_id']:
    customer_data = customer_profile[customer_profile['customer_id'] == customer_id].iloc[0]
    is_churned = churn_labels[churn_labels['customer_id'] == customer_id]['churned'].values[0]
    
    # Initialisiere Issue-Liste für diesen Kunden
    customer_technical_issues[customer_id] = []
    
    # Mehr Logs für Kunden mit Problemen
    n_logs = random.randint(20, 50)
    
    for i in range(n_logs):
        timestamp = datetime(2026, 3, 1) - timedelta(days=random.randint(1, 90))
        
        # Baseline Qualität (gut)
        speed_factor = random.uniform(0.85, 1.0)
        packet_loss = random.uniform(0, 2)
        latency = random.uniform(10, 40)
        downtime = 0
        drops = 0
        
        # Zufällige technische Probleme mit bestimmter Wahrscheinlichkeit
        problem_type = None
        
        # 20% Chance für technische Probleme (höher bei abgewanderten Kunden)
        problem_chance = 0.35 if is_churned else 0.15
        
        if random.random() < problem_chance:
            problem_type = np.random.choice([
                'slow_speed',
                'connection_drops',
                'high_latency',
                'outage',
                'packet_loss'
            ], p=[0.3, 0.15, 0.25, 0.1, 0.20])
            
            # Simuliere verschiedene Problemtypen
            if problem_type == 'slow_speed':
                speed_factor = random.uniform(0.3, 0.7)
                latency = random.uniform(50, 150)
                packet_loss = random.uniform(1, 2)
                
            elif problem_type == 'connection_drops':
                drops = random.randint(3, 15)
                packet_loss = random.uniform(2, 8)
                latency = random.uniform(80, 200)
                speed_factor = random.uniform(0.6, 0.9)
                
            elif problem_type == 'high_latency':
                latency = random.uniform(150, 500)
                speed_factor = random.uniform(0.7, 0.95)
                
            elif problem_type == 'outage':
                downtime = random.randint(60, 300)
                speed_factor = 0
                drops = random.randint(50, 200)
                packet_loss = 100
                latency = 0
                
            elif problem_type == 'packet_loss':
                packet_loss = random.uniform(5, 25)
                latency = random.uniform(50, 120)
                speed_factor = random.uniform(0.5, 0.8)
                drops = random.randint(1, 5)
            
            # Speichere dieses Problem-Event
            customer_technical_issues[customer_id].append({
                'timestamp': timestamp,
                'problem_type': problem_type
            })
            

        connection_logs.append({
            'timestamp': timestamp,
            'issue_detected': 'error: ' + problem_type if problem_type else 'none'
            'customer_id': customer_id,
            'speed_measured_mbps': round(customer_data['speed_tier_mbps'] * speed_factor, 1),
            'packet_loss_percent': round(packet_loss, 2),
            'latency_ms': round(latency, 1),
            'downtime_minutes': downtime,
            'connection_drops_count': drops
        })
        
        log_id += 1

connection_quality_logs = pd.DataFrame(connection_logs)

print(f"Connection Logs erstellt: {len(connection_quality_logs)} Logs")
print(f"Davon mit Problemen: {len(connection_quality_logs[connection_quality_logs['issue_detected'] != 'none'])}")



# Tickets


ticket_templates = {
    'slow_speed': [
        "Internet is extremely slow, only getting {actual_speed} Mbps instead of {expected_speed} Mbps",
        "Speed test shows terrible results - {actual_speed} Mbps when I'm paying for {expected_speed} Mbps",
        "Pages are loading very slowly, speed is way below what was promised",
        "Streaming keeps buffering, internet speed is insufficient"
    ],
    'connection_drops': [
        "Internet keeps disconnecting every few minutes",
        "Connection drops constantly, can't stay online",
        "WiFi keeps cutting out throughout the day",
        "Losing connection repeatedly, very frustrating"
    ],
    'high_latency': [
        "Terrible lag during video calls, latency is {latency}ms",
        "High ping, gaming is impossible with this latency",
        "Response time is awful, everything is delayed",
        "Video conferences are choppy, high latency issues"
    ],
    'outage': [
        "Complete outage for {downtime} minutes, no internet at all",
        "Internet has been down for over an hour",
        "Total service interruption in my area",
        "No connection whatsoever, lights on router are red"
    ],
    'packet_loss': [
        "Experiencing severe packet loss ({packet_loss}%), connection is unstable",
        "Data is getting lost, packet loss is very high",
        "Connection quality is terrible, lots of packet loss",
        "Unstable connection with frequent data loss"
    ],
    'billing': [
        "Charged ${amount} but my plan should be ${plan_price}",
        "Why did my bill increase without notice?",
        "Double charged this month",
        "Need explanation for additional fees on bill"
    ],
    'service_change': [
        "Want to upgrade to faster plan",
        "Need to downgrade to save money",
        "How do I cancel my service?",
        "Moving to new address, how to transfer service?"
    ],
    'sales': [
        "Competitor is offering better price, can you match?",
        "What promotions do you currently have?",
        "Interested in bundling services"
    ]
}

tickets = []
ticket_id = 1

for customer_id in customer_profile['customer_id']:
    customer_data = customer_profile[customer_profile['customer_id'] == customer_id].iloc[0]
    is_churned = churn_labels[churn_labels['customer_id'] == customer_id]['churned'].values[0]
    
    # Hole technische Probleme für diesen Kunden
    tech_issues = customer_technical_issues[customer_id]
    
    # Generiere Tickets basierend auf tatsächlichen Problemen
    # 70% der technischen Probleme führen zu einem Support Ticket
    tickets_from_issues = [issue for issue in tech_issues if random.random() < 0.7]
    
    # Füge noch zufällige andere Tickets hinzu (billing, service_change, etc.)
    if is_churned:
        n_other_tickets = random.randint(2, 5)
    else:
        n_other_tickets = random.randint(0, 3)
    
    # 1. TICKETS BASIEREND AUF TECHNISCHEN PROBLEMEN
    for issue in tickets_from_issues:
        problem_type = issue['problem_type']
        
        # Ticket wird 0-24 Stunden nach dem Problem erstellt
        ticket_timestamp = issue['timestamp'] + timedelta(hours=random.randint(0, 12))
        
        template = random.choice(ticket_templates[problem_type])
        
        # Hole die tatsächlichen Werte aus dem Connection Log
        log_data = connection_quality_logs[
            connection_quality_logs['log_id'] == issue['log_id']
        ].iloc[0]
        
        description = template.format(
            actual_speed=int(log_data['speed_measured_mbps']),
            expected_speed=customer_data['speed_tier_mbps'],
            latency=int(log_data['latency_ms']),
            downtime=log_data['downtime_minutes'],
            packet_loss=round(log_data['packet_loss_percent'], 1)
        )
        
        # Technische Tickets dauern länger zu lösen
        if issue['severity'] == 'high':
            solved_hours = random.randint(12, 120)
            priority = random.choice(['high', 'urgent'])
        else:
            solved_hours = random.randint(1, 48)
            priority = random.choice(['medium', 'high'])
        
        timestamp_closed = ticket_timestamp + timedelta(hours=solved_hours)
        
        tickets.append({
            'ticket_id': f'TKT_{ticket_id:06d}',
            'customer_id': customer_id,
            'timestamp_created': ticket_timestamp,
            'timestamp_closed': timestamp_closed,
            'subject': f"Technical Issue - {problem_type.replace('_', ' ').title()}",
            'description': description,
            'category': 'technical',
            'priority': priority,
            'channel': random.choice(['email', 'chat', 'phone', 'web_form']),
            'status': 'closed',
            'solved_in_hours': solved_hours,
            'related_log_id': issue['log_id'],
            'technical_issue_type': problem_type
        })
        ticket_id += 1
    
    # 2. ANDERE TICKETS (billing, service_change, sales)
    for _ in range(n_other_tickets):
        category = random.choices(
            ['billing', 'service_change', 'sales'],
            weights=[0.5, 0.35, 0.15]
        )[0]
        
        # Abgewanderte Kunden haben mehr "service_change" Tickets
        if is_churned and random.random() > 0.4:
            category = 'service_change'
        
        template = random.choice(ticket_templates[category])
        
        description = template.format(
            amount=round(customer_data['monthly_bill'] * random.uniform(1.1, 1.5), 2),
            plan_price=customer_data['monthly_bill']
        )
        
        timestamp_created = datetime(2026, 3, 1) - timedelta(days=random.randint(1, 180))
        
        if category == 'billing':
            solved_hours = random.randint(1, 48)
            priority = random.choice(['low', 'medium', 'high'])
        else:
            solved_hours = random.randint(1, 24)
            priority = random.choice(['low', 'medium'])
        
        timestamp_closed = timestamp_created + timedelta(hours=solved_hours)
        
        tickets.append({
            'ticket_id': f'TKT_{ticket_id:06d}',
            'customer_id': customer_id,
            'timestamp_created': timestamp_created,
            'timestamp_closed': timestamp_closed,
            'subject': category.replace('_', ' ').title(),
            'description': description,
            'category': category,
            'priority': priority,
            'channel': random.choice(['email', 'chat', 'phone', 'web_form']),
            'status': 'closed',
            'solved_in_hours': solved_hours,
            'related_log_id': None,
            'technical_issue_type': None
        })
        
        ticket_id += 1

support_tickets = pd.DataFrame(tickets)

print(f"Support Tickets erstellt: {len(support_tickets)} Tickets")
print(f"Davon technische Tickets: {len(support_tickets[support_tickets['category'] == 'technical'])}")
print(f"Mit Log-Verknüpfung: {support_tickets['related_log_id'].notna().sum()}")



# Chat Transcripts


CREDENTIALS_PATH = '/home/stsc/projects/testscript_nina/abatag-gcp-ai-online-p-1092b26f2327.json'
GCP_PROJECT = os.getenv("GCP_PROJECT", "abatag-gcp-ai-online-p")
GCP_LOCATION = os.getenv("GCP_LOCATION", "global")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-pro-preview")


def setup_agent() -> Agent:
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_PATH,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    provider = GoogleProvider(
        credentials=credentials,
        project=GCP_PROJECT,
        location=GCP_LOCATION,
    )
    model = GoogleModel(GEMINI_MODEL, provider=provider)
    Agent.instrument_all()
    return Agent(model=model, instrument=True)


def parse_json_response(raw_text):
    cleaned = raw_text.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    return json.loads(cleaned)


def build_gemini_chat_library(agent, total_chats=60):
    if not os.path.exists(CREDENTIALS_PATH):
        raise ValueError(
            f"Service-Account-Datei nicht gefunden: {CREDENTIALS_PATH}"
        )

    prompt = f"""
Erstelle {total_chats} realistische ISP-Support-Chats als JSON.

WICHTIG:
- Gib NUR valides JSON zurück, ohne Markdown, ohne Codeblock.
- Sprache: Deutsch.
- Jeder Chat muss eine realistische Kunde-Agent Interaktion sein.
- Themenverteilung: mindestens 65% technische Internetprobleme, Rest Vertrag/Billing/Zahlung.
- Jeder Chat enthält 6 bis 10 Nachrichten.
- Nachrichten sollen abwechselnd von customer und agent kommen.

Gewünschtes JSON-Schema:
{{
  "chats": [
    {{
      "topic": "technical|contract|billing|payment",
      "messages": [
        {{"speaker": "customer", "message": "..."}},
        {{"speaker": "agent", "message": "..."}}
      ]
    }}
  ]
}}
""".strip()

    result = agent.run_sync(prompt)
    payload = parse_json_response(str(result.output))
    chats = payload.get("chats", [])

    if not chats:
        raise ValueError("Gemini hat keine Chats im erwarteten Format zurückgegeben.")

    categorized = {
        "technical": [],
        "contract": [],
        "billing": [],
        "payment": [],
    }

    for chat in chats:
        topic = str(chat.get("topic", "technical")).lower().strip()
        messages = chat.get("messages", [])

        if topic not in categorized:
            topic = "technical"

        valid_messages = []
        for msg in messages:
            speaker = str(msg.get("speaker", "")).strip().lower()
            message_text = str(msg.get("message", "")).strip()

            if speaker not in {"customer", "agent"}:
                continue
            if not message_text:
                continue

            valid_messages.append(
                {
                    "speaker": speaker,
                    "message": message_text,
                }
            )

        if len(valid_messages) >= 4:
            categorized[topic].append(valid_messages)

    if not categorized["technical"]:
        raise ValueError("Gemini hat keine verwertbaren technischen Chats geliefert.")

    # Falls einzelne Themen fehlen, werden technische Chats als Fallback genutzt.
    for topic in ["contract", "billing", "payment"]:
        if not categorized[topic]:
            categorized[topic] = categorized["technical"]

    return categorized


def add_timestamps(base_messages, timestamp_start):
    enriched = []
    for idx, msg in enumerate(base_messages):
        enriched.append(
            {
                "speaker": msg["speaker"],
                "timestamp": (timestamp_start + timedelta(minutes=2 * idx)).isoformat(),
                "message": msg["message"],
            }
        )
    return enriched


chat_transcripts = []
session_id = 1

chat_agent = setup_agent()
chat_library = build_gemini_chat_library(agent=chat_agent, total_chats=60)

topic_cursor = {
    "technical": 0,
    "contract": 0,
    "billing": 0,
    "payment": 0,
}

# Deterministisch: jeder 3. Kunde bekommt Chats
customers_with_chats = customer_profile["customer_id"].iloc[::3].tolist()

for customer_idx, customer_id in enumerate(customers_with_chats):
    is_churned = churn_labels[churn_labels["customer_id"] == customer_id][
        "churned"
    ].values[0]
    tech_issues = sorted(
        customer_technical_issues[customer_id],
        key=lambda x: x["timestamp"],
        reverse=True,
    )

    technical_chat_count = 2 if is_churned and len(tech_issues) > 1 else 1
    technical_chat_count = min(technical_chat_count, len(tech_issues))

    # Primär technische Chats
    for issue_idx in range(technical_chat_count):
        issue = tech_issues[issue_idx]
        log_data = connection_quality_logs[
            connection_quality_logs["log_id"] == issue["log_id"]
        ].iloc[0]

        timestamp_start = issue["timestamp"] + timedelta(hours=(customer_idx % 6))
        template_idx = topic_cursor["technical"] % len(chat_library["technical"])
        base_messages = [dict(m) for m in chat_library["technical"][template_idx]]
        topic_cursor["technical"] += 1

        base_messages[0]["message"] = (
            f"{base_messages[0]['message']}"
        )

        messages = add_timestamps(base_messages, timestamp_start)
        timestamp_end = timestamp_start + timedelta(minutes=2 * (len(messages) - 1))

        chat_transcripts.append(
            {
                "session_id": f"CHAT_{session_id:05d}",
                "customer_id": customer_id,
                "timestamp_start": timestamp_start,
                "timestamp_end": timestamp_end,
                "messages": json.dumps(messages),
                "agent_id": f"AGENT_{(customer_idx % 20) + 1:03d}",
            }
        )
        session_id += 1

    # Sekundäre Vertrags-/Billing-/Zahlungschats
    include_other_chat = (customer_idx % 3 == 0)
    if include_other_chat:
        other_topic_cycle = ["billing", "contract", "payment"]
        other_topic = other_topic_cycle[customer_idx % len(other_topic_cycle)]

        template_idx = topic_cursor[other_topic] % len(chat_library[other_topic])
        base_messages = [dict(m) for m in chat_library[other_topic][template_idx]]
        topic_cursor[other_topic] += 1

        timestamp_start = datetime(2026, 3, 1) - timedelta(days=((customer_idx * 7) % 180))
        messages = add_timestamps(base_messages, timestamp_start)
        timestamp_end = timestamp_start + timedelta(minutes=2 * (len(messages) - 1))

        chat_transcripts.append(
            {
                "session_id": f"CHAT_{session_id:05d}",
                "customer_id": customer_id,
                "timestamp_start": timestamp_start,
                "timestamp_end": timestamp_end,
                "messages": json.dumps(messages),
                "agent_id": f"AGENT_{((customer_idx + 5) % 20) + 1:03d}",
            }
        )
        session_id += 1

chat_transcripts_df = pd.DataFrame(chat_transcripts)

print(f"\nChat Transcripts erstellt: {len(chat_transcripts_df)} Chats")

chat_transcripts_df.to_excel("chat_transcripts.xlsx", index=False)
