from uuid import uuid4

import structlog

from server.db import ProductTable, db

logger = structlog.getLogger(__name__)


def make_shop(
    customer_id=DEFAULT_CUSTOMER,
    email="teamx@ncsc.nl",
    chamber_of_commerce_number="69599076",
    product_name="NIS2 Publiek",  # or "NIS2 Portaal"
    insync=True,
    importance=Nis2Importance.ESSENTIAL,
    appointed=None,
    entity_id=None,
    entity_name=None,
    entity_csirt_id=uuid4(),
    entity_csirt_name="Stichting Remy",
    entity_regulator_id=uuid4(),
    entity_regulator_name="Stichting Remy",
    crm_company_id=1,
    crm_person_id=1,
    lifecycle_state=SubscriptionLifecycle.ACTIVE,
):
    """Service port fixture.

    Returns: The subscription_id of the created fixture.
    """
    if not entity_id:
        entity_id = uuid4()
    if not entity_name:
        entity_name = "entity name"

    product = ProductTable.query.filter(ProductTable.name == product_name).one()
    description = (
        "Mocked test description"
        if lifecycle_state == SubscriptionLifecycle.ACTIVE
        else initial_subscription_description(chamber_of_commerce_number, email, product_name)
    )
    subscription = Nis2Inactive.from_product_id(
        product_id=product.product_id,
        customer_id=customer_id,
        status=SubscriptionLifecycle.INITIAL,
        insync=insync,
    )
    subscription.description = description
    subscription.nis2.importance = importance
    subscription.nis2.appointed = appointed
    subscription.nis2.company.chamber_of_commerce_number = chamber_of_commerce_number
    subscription.nis2.company.chamber_of_commerce_name = "Test bedrijf"
    subscription.nis2.company.crm_company_name = "Test bedrijf"
    subscription.nis2.company.crm_company_id = crm_person_id
    subscription.nis2.entity.entity_id = entity_id
    subscription.nis2.entity.entity_name = entity_name
    subscription.nis2.contacts.append(
        ContactBlockInactive.new(
            subscription_id=subscription.subscription_id,
            name="Contact 1",
            entity_contact_id=uuid4(),
            crm_person_id=crm_person_id,
        )
    )
    subscription.nis2.csirt = CsirtBlockInactive.new(
        subscription_id=subscription.subscription_id,
        name="CSIRT",
        entity_csirt_id=entity_csirt_id,
        entity_csirt_name=entity_csirt_name,
        crm_company_id=2,
    )
    regulator = RegulatorBlockInactive.new(
        subscription_id=subscription.subscription_id,
        name="Regulator",
        entity_regulator_id=entity_regulator_id,
        entity_regulator_name=entity_regulator_name,
        crm_company_id=3,
    )
    subscription.nis2.regulators.append(regulator)

    subscription.save()
    subscription = SubscriptionModel.from_other_lifecycle(subscription, SubscriptionLifecycle.ACTIVE)
    subscription.save()
    db.session.commit()

    return str(subscription.subscription_id)
