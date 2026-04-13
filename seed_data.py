"""
Seed script: emits dummy metadata to DataHub for testing the custom home page.
Run with: python seed_data.py
"""
import time
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.metadata.schema_classes import (
    ChangeAuditStampsClass,
    # Domains
    DomainPropertiesClass,
    DomainsClass,
    # Datasets
    DatasetPropertiesClass,
    SchemaMetadataClass,
    SchemaFieldClass,
    SchemaFieldDataTypeClass,
    StringTypeClass,
    NumberTypeClass,
    BooleanTypeClass,
    DateTypeClass,
    OtherSchemaClass,
    # Ownership
    OwnershipClass,
    OwnerClass,
    OwnershipTypeClass,
    # Tags
    GlobalTagsClass,
    TagAssociationClass,
    TagPropertiesClass,
    # Glossary
    GlossaryTermInfoClass,
    GlossaryNodeInfoClass,
    GlossaryTermsClass,
    GlossaryTermAssociationClass,
    # Dashboards
    DashboardInfoClass,
    # Data Platform
    DataPlatformInfoClass,
    PlatformTypeClass,
    # Institutional Memory
    InstitutionalMemoryClass,
    InstitutionalMemoryMetadataClass,
    AuditStampClass,
)
from datahub.metadata.com.linkedin.pegasus2avro.common import Status

GMS_URL = "http://localhost:8080"
emitter = DatahubRestEmitter(GMS_URL)

now_ms = int(time.time() * 1000)
system_actor = "urn:li:corpuser:datahub"
audit = AuditStampClass(time=now_ms, actor=system_actor)
change_audit = ChangeAuditStampsClass(created=audit, lastModified=audit)


def emit(urn, aspect):
    mcp = MetadataChangeProposalWrapper(entityUrn=urn, aspect=aspect)
    emitter.emit(mcp)


def make_field(name, dtype_class, description=""):
    return SchemaFieldClass(
        fieldPath=name,
        type=SchemaFieldDataTypeClass(type=dtype_class()),
        nativeDataType=dtype_class.__name__.replace("Class", "").lower(),
        description=description,
    )


print("Seeding domains...")
domains = {
    "finance":    ("urn:li:domain:finance",    "Finance",    "Financial reporting and revenue data"),
    "marketing":  ("urn:li:domain:marketing",  "Marketing",  "Campaign performance and customer analytics"),
    "engineering":("urn:li:domain:engineering","Engineering","Product telemetry and infrastructure metrics"),
    "hr":         ("urn:li:domain:hr",         "HR",         "People and workforce analytics"),
}
for key, (urn, name, desc) in domains.items():
    emit(urn, DomainPropertiesClass(name=name, description=desc))
print(f"  Created {len(domains)} domains")


print("Seeding glossary terms...")
emit("urn:li:glossaryNode:metrics", GlossaryNodeInfoClass(name="Metrics", definition="Key business metrics"))
glossary_terms = [
    ("urn:li:glossaryTerm:metrics.mau", "Monthly Active Users", "Count of unique users active in a 30-day window"),
    ("urn:li:glossaryTerm:metrics.arpu", "Average Revenue Per User", "Total revenue divided by number of active users"),
    ("urn:li:glossaryTerm:metrics.churn", "Churn Rate", "Percentage of customers who stopped using the product"),
    ("urn:li:glossaryTerm:metrics.ltv", "Customer Lifetime Value", "Predicted net profit from the entire relationship with a customer"),
    ("urn:li:glossaryTerm:metrics.cac", "Customer Acquisition Cost", "Cost to acquire a new customer"),
]
for urn, name, definition in glossary_terms:
    emit(urn, GlossaryTermInfoClass(
        name=name,
        definition=definition,
        termSource="INTERNAL",
        parentNode="urn:li:glossaryNode:metrics",
    ))
print(f"  Created {len(glossary_terms)} glossary terms")


print("Seeding datasets...")
datasets = [
    # Finance
    {
        "urn": "urn:li:dataset:(urn:li:dataPlatform:snowflake,finance.revenue.monthly_summary,PROD)",
        "name": "monthly_summary",
        "platform": "urn:li:dataPlatform:snowflake",
        "description": "Monthly revenue aggregated by product and region",
        "domain": "urn:li:domain:finance",
        "fields": [
            make_field("month", DateTypeClass, "Reporting month"),
            make_field("product_line", StringTypeClass, "Product line name"),
            make_field("region", StringTypeClass, "Geographic region"),
            make_field("revenue_usd", NumberTypeClass, "Total revenue in USD"),
            make_field("transactions", NumberTypeClass, "Number of transactions"),
        ],
        "tags": ["urn:li:tag:revenue", "urn:li:tag:certified"],
        "terms": ["urn:li:glossaryTerm:metrics.arpu"],
    },
    {
        "urn": "urn:li:dataset:(urn:li:dataPlatform:snowflake,finance.revenue.daily_transactions,PROD)",
        "name": "daily_transactions",
        "platform": "urn:li:dataPlatform:snowflake",
        "description": "Raw daily transaction log",
        "domain": "urn:li:domain:finance",
        "fields": [
            make_field("transaction_id", StringTypeClass, "Unique transaction ID"),
            make_field("customer_id", StringTypeClass),
            make_field("amount_usd", NumberTypeClass),
            make_field("currency", StringTypeClass),
            make_field("created_at", DateTypeClass),
            make_field("status", StringTypeClass, "pending | completed | refunded"),
        ],
        "tags": ["urn:li:tag:pii"],
        "terms": [],
    },
    # Marketing
    {
        "urn": "urn:li:dataset:(urn:li:dataPlatform:bigquery,marketing.campaigns.performance,PROD)",
        "name": "performance",
        "platform": "urn:li:dataPlatform:bigquery",
        "description": "Campaign-level performance metrics updated daily",
        "domain": "urn:li:domain:marketing",
        "fields": [
            make_field("campaign_id", StringTypeClass),
            make_field("campaign_name", StringTypeClass),
            make_field("channel", StringTypeClass, "email | paid_search | social"),
            make_field("impressions", NumberTypeClass),
            make_field("clicks", NumberTypeClass),
            make_field("conversions", NumberTypeClass),
            make_field("spend_usd", NumberTypeClass),
            make_field("date", DateTypeClass),
        ],
        "tags": ["urn:li:tag:certified"],
        "terms": ["urn:li:glossaryTerm:metrics.cac"],
    },
    {
        "urn": "urn:li:dataset:(urn:li:dataPlatform:bigquery,marketing.users.active_users,PROD)",
        "name": "active_users",
        "platform": "urn:li:dataPlatform:bigquery",
        "description": "Daily and monthly active user counts by segment",
        "domain": "urn:li:domain:marketing",
        "fields": [
            make_field("date", DateTypeClass),
            make_field("segment", StringTypeClass),
            make_field("dau", NumberTypeClass, "Daily active users"),
            make_field("mau", NumberTypeClass, "Monthly active users"),
            make_field("wau", NumberTypeClass, "Weekly active users"),
        ],
        "tags": ["urn:li:tag:certified"],
        "terms": ["urn:li:glossaryTerm:metrics.mau", "urn:li:glossaryTerm:metrics.churn"],
    },
    # Engineering
    {
        "urn": "urn:li:dataset:(urn:li:dataPlatform:kafka,engineering.events.page_view,PROD)",
        "name": "page_view",
        "platform": "urn:li:dataPlatform:kafka",
        "description": "Real-time page view events from the web app",
        "domain": "urn:li:domain:engineering",
        "fields": [
            make_field("event_id", StringTypeClass),
            make_field("user_id", StringTypeClass),
            make_field("session_id", StringTypeClass),
            make_field("page", StringTypeClass),
            make_field("timestamp_ms", NumberTypeClass),
            make_field("country", StringTypeClass),
        ],
        "tags": ["urn:li:tag:streaming", "urn:li:tag:pii"],
        "terms": [],
    },
    {
        "urn": "urn:li:dataset:(urn:li:dataPlatform:postgres,engineering.app.users,PROD)",
        "name": "users",
        "platform": "urn:li:dataPlatform:postgres",
        "description": "Core users table — source of truth for user accounts",
        "domain": "urn:li:domain:engineering",
        "fields": [
            make_field("id", StringTypeClass, "UUID primary key"),
            make_field("email", StringTypeClass),
            make_field("name", StringTypeClass),
            make_field("created_at", DateTypeClass),
            make_field("is_active", BooleanTypeClass),
            make_field("plan", StringTypeClass, "free | pro | enterprise"),
        ],
        "tags": ["urn:li:tag:pii", "urn:li:tag:source-of-truth"],
        "terms": ["urn:li:glossaryTerm:metrics.ltv"],
    },
    # HR
    {
        "urn": "urn:li:dataset:(urn:li:dataPlatform:snowflake,hr.workforce.headcount,PROD)",
        "name": "headcount",
        "platform": "urn:li:dataPlatform:snowflake",
        "description": "Monthly headcount by department and level",
        "domain": "urn:li:domain:hr",
        "fields": [
            make_field("month", DateTypeClass),
            make_field("department", StringTypeClass),
            make_field("level", StringTypeClass),
            make_field("headcount", NumberTypeClass),
            make_field("new_hires", NumberTypeClass),
            make_field("attrition", NumberTypeClass),
        ],
        "tags": ["urn:li:tag:confidential"],
        "terms": [],
    },
]

# Emit tags first
all_tags = set()
for d in datasets:
    all_tags.update(d["tags"])
for tag_urn in all_tags:
    tag_name = tag_urn.split(":")[-1].replace("-", " ").title()
    emit(tag_urn, TagPropertiesClass(name=tag_name))

for d in datasets:
    urn = d["urn"]
    emit(urn, DatasetPropertiesClass(
        name=d["name"],
        description=d["description"],
        customProperties={"tier": "gold" if "certified" in str(d["tags"]) else "silver"},
    ))
    emit(urn, SchemaMetadataClass(
        schemaName=d["name"],
        platform=d["platform"],
        version=0,
        hash="",
        platformSchema=OtherSchemaClass(rawSchema=""),
        fields=d["fields"],
    ))
    emit(urn, DomainsClass(domains=[d["domain"]]))
    if d["tags"]:
        emit(urn, GlobalTagsClass(tags=[TagAssociationClass(tag=t) for t in d["tags"]]))
    if d["terms"]:
        emit(urn, GlossaryTermsClass(
            terms=[GlossaryTermAssociationClass(urn=t) for t in d["terms"]],
            auditStamp=audit,
        ))
    emit(urn, OwnershipClass(
        owners=[OwnerClass(owner=system_actor, type=OwnershipTypeClass.DATAOWNER)],
        lastModified=audit,
    ))

print(f"  Created {len(datasets)} datasets")


print("Seeding dashboards...")
dashboards = [
    {
        "urn": "urn:li:dashboard:(looker,finance-overview)",
        "title": "Finance Overview",
        "description": "Executive finance dashboard with revenue, ARR, and churn metrics",
        "domain": "urn:li:domain:finance",
        "tags": ["urn:li:tag:certified"],
    },
    {
        "urn": "urn:li:dashboard:(looker,marketing-performance)",
        "title": "Marketing Performance",
        "description": "Campaign ROI, CAC, and funnel metrics across all channels",
        "domain": "urn:li:domain:marketing",
        "tags": ["urn:li:tag:certified"],
    },
    {
        "urn": "urn:li:dashboard:(looker,product-engagement)",
        "title": "Product Engagement",
        "description": "DAU/MAU, retention curves, and feature adoption tracking",
        "domain": "urn:li:domain:engineering",
        "tags": [],
    },
    {
        "urn": "urn:li:dashboard:(looker,hr-headcount)",
        "title": "HR Headcount",
        "description": "Hiring, attrition, and org structure by department",
        "domain": "urn:li:domain:hr",
        "tags": ["urn:li:tag:confidential"],
    },
]
for d in dashboards:
    emit(d["urn"], DashboardInfoClass(
        title=d["title"],
        description=d["description"],
        lastModified=change_audit,
    ))
    emit(d["urn"], DomainsClass(domains=[d["domain"]]))
    if d["tags"]:
        emit(d["urn"], GlobalTagsClass(tags=[TagAssociationClass(tag=t) for t in d["tags"]]))
print(f"  Created {len(dashboards)} dashboards")


print("\nDone! Summary:")
print(f"  {len(domains)} domains")
print(f"  {len(glossary_terms)} glossary terms")
print(f"  {len(datasets)} datasets (Snowflake, BigQuery, Kafka, Postgres)")
print(f"  {len(dashboards)} dashboards (Looker)")
print("\nRefresh DataHub at http://localhost:3001")
