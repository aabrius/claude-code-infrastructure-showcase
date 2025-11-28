# Google Ad Manager SOAP API v202511 - Labels & Custom Fields

**Last Updated:** 2025-11-28
**API Version:** v202511
**Namespace:** `https://www.google.com/apis/ads/publisher/v202511`

This document provides comprehensive reference documentation for the Labels and Custom Fields category of the Google Ad Manager SOAP API. These services enable publishers to organize, categorize, and extend entity data with custom metadata.

---

## Table of Contents

1. [Overview](#overview)
2. [LabelService](#labelservice)
   - [Methods](#labelservice-methods)
   - [Label Object - Complete Field Reference](#label-object---complete-field-reference)
   - [LabelType Enum - Complete Reference](#labeltype-enum---complete-reference)
   - [AdCategoryDto Object](#adcategorydto-object)
   - [AppliedLabel Object](#appliedlabel-object)
   - [LabelAction Types](#labelaction-types)
   - [PQL Filtering for Labels](#pql-filtering-for-labels)
3. [CustomFieldService](#customfieldservice)
   - [Methods](#customfieldservice-methods)
   - [CustomField Object - Complete Field Reference](#customfield-object---complete-field-reference)
   - [DropDownCustomField Object](#dropdowncustomfield-object)
   - [CustomFieldOption Object](#customfieldoption-object)
   - [CustomFieldEntityType Enum - Complete Reference](#customfieldentitytype-enum---complete-reference)
   - [CustomFieldDataType Enum - Complete Reference](#customfielddatatype-enum---complete-reference)
   - [CustomFieldVisibility Enum - Complete Reference](#customfieldvisibility-enum---complete-reference)
   - [CustomFieldAction Types](#customfieldaction-types)
   - [PQL Filtering for Custom Fields](#pql-filtering-for-custom-fields)
4. [CustomFieldValue Usage](#customfieldvalue-usage)
   - [CustomFieldValue Object](#customfieldvalue-object)
   - [DropDownCustomFieldValue Object](#dropdowncustomfieldvalue-object)
   - [Setting Custom Field Values on Entities](#setting-custom-field-values-on-entities)
5. [Label Application to Entities](#label-application-to-entities)
6. [Custom Fields in Reporting](#custom-fields-in-reporting)
7. [Python Code Examples](#python-code-examples)
8. [Best Practices](#best-practices)
9. [Error Handling](#error-handling)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The Labels and Custom Fields category contains two services that enable publishers to organize and extend their Ad Manager data:

| Service | Purpose | Key Capabilities |
|---------|---------|------------------|
| **LabelService** | Label management | Create labels for competitive exclusion, frequency capping, ad exclusion, creative wrapping |
| **CustomFieldService** | Custom field management | Create custom metadata fields for orders, line items, creatives, proposals |

### Use Cases

**Labels:**
- **Competitive Exclusion**: Prevent ads from competing advertisers showing on the same page
- **Ad Unit Frequency Capping**: Limit how often users see certain ad types on specific inventory
- **Ad Exclusion**: Block specific ads from appearing on tagged inventory
- **Creative Wrapping**: Force header/footer creatives around delivered ads
- **Canonical Categories**: Map labels to Google ad categories for cross-system blocking

**Custom Fields:**
- Track internal campaign identifiers (IO numbers, campaign codes)
- Store client-specific metadata (agency names, billing codes)
- Add workflow states (approval status, priority level)
- Enable custom reporting dimensions

### Service Access Pattern

```python
from googleads import ad_manager

# Initialize client
client = ad_manager.AdManagerClient.LoadFromStorage('googleads.yaml')

# Get service instances
label_service = client.GetService('LabelService', version='v202511')
custom_field_service = client.GetService('CustomFieldService', version='v202511')
```

### WSDL Locations

```
https://ads.google.com/apis/ads/publisher/v202511/LabelService?wsdl
https://ads.google.com/apis/ads/publisher/v202511/CustomFieldService?wsdl
```

---

## LabelService

**WSDL:** `https://ads.google.com/apis/ads/publisher/v202511/LabelService?wsdl`

Provides operations for creating and managing Label objects. Labels are used to group and categorize entities for competitive exclusion, frequency capping, ad blocking, and creative wrapping.

### LabelService Methods

#### createLabels

Creates new Label objects in the network.

```
createLabels(labels: Label[]) -> Label[]
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `labels` | `Label[]` | Yes | Array of Label objects to create |

**Required Fields for Creation:**
- `name` - Label name (max 127 characters)
- `types` - Array of LabelType values

**Returns:** `Label[]` - Created labels with server-assigned `id` values

**Example:**
```python
# Create a competitive exclusion label
label = {
    'name': 'Automotive Brands',
    'description': 'Prevents competing auto brands from showing together',
    'types': ['COMPETITIVE_EXCLUSION']
}

result = label_service.createLabels([label])
print(f"Created label ID: {result[0]['id']}")
```

---

#### getLabelsByStatement

Retrieves Label objects matching a PQL query.

```
getLabelsByStatement(filterStatement: Statement) -> LabelPage
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `filterStatement` | `Statement` | Yes | PQL query with optional pagination |

**Returns:** `LabelPage` - Contains `results` array and `totalResultSetSize`

**Example:**
```python
# Get all active competitive exclusion labels
statement = ad_manager.StatementBuilder(version='v202511')
statement.Where("isActive = true AND type = 'COMPETITIVE_EXCLUSION'")
statement.Limit(100)

response = label_service.getLabelsByStatement(statement.ToStatement())
for label in response['results']:
    print(f"Label: {label['name']} (ID: {label['id']})")
```

---

#### updateLabels

Updates existing Label objects.

```
updateLabels(labels: Label[]) -> Label[]
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `labels` | `Label[]` | Yes | Array of Label objects with updated fields |

**Required Fields:**
- `id` - Existing label ID

**Updatable Fields:**
- `name`
- `description`
- `types` (can add types, but cannot remove if in use)

**Returns:** `Label[]` - Updated label objects

**Example:**
```python
# Update label description
label = label_service.getLabelsByStatement(
    ad_manager.StatementBuilder().Where("id = :id").WithBindVariable('id', 12345).ToStatement()
)['results'][0]

label['description'] = 'Updated description for automotive brands'
updated = label_service.updateLabels([label])
```

---

#### performLabelAction

Performs bulk actions on Label objects matching a query.

```
performLabelAction(labelAction: LabelAction, filterStatement: Statement) -> UpdateResult
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `labelAction` | `LabelAction` | Yes | Action to perform (ActivateLabels, DeactivateLabels) |
| `filterStatement` | `Statement` | Yes | PQL query selecting labels to act on |

**Returns:** `UpdateResult` - Contains `numChanges` field

**Example:**
```python
# Deactivate all labels with specific name pattern
statement = ad_manager.StatementBuilder()
statement.Where("name LIKE 'Deprecated%'")

action = {'xsi_type': 'DeactivateLabels'}
result = label_service.performLabelAction(action, statement.ToStatement())
print(f"Deactivated {result['numChanges']} labels")
```

---

### Label Object - Complete Field Reference

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `id` | `xsd:long` | - | Yes | Unique identifier assigned by Google |
| `name` | `xsd:string` | Yes | No | Label name. Max 127 characters. Must be unique within the network |
| `description` | `xsd:string` | No | No | Optional description. Max 255 characters |
| `isActive` | `xsd:boolean` | - | Yes | Whether the label is active. Controlled via performLabelAction |
| `adCategory` | `AdCategoryDto` | No | No | Associated Google canonical ad category. Only valid for CANONICAL_CATEGORY type |
| `types` | `LabelType[]` | Yes | No | Array of label types this label supports. A label can have multiple types |

**Field Details:**

**id**
- Automatically assigned when label is created
- Used to reference the label when applying to entities
- Immutable after creation

**name**
- Must be unique within the network
- Used for display in UI and reports
- Case-sensitive for uniqueness

**types**
- A single label can have multiple types
- Once a type is in use (applied to entities), it cannot be removed
- New types can be added to existing labels

---

### LabelType Enum - Complete Reference

| Value | Description | Use Case |
|-------|-------------|----------|
| `COMPETITIVE_EXCLUSION` | Prevents ads with the same label from showing on the same page | Apply to line items from competing advertisers (e.g., Ford vs. Toyota). Only one line item with a given competitive exclusion label can serve per page |
| `AD_UNIT_FREQUENCY_CAP` | Limits how frequently a user sees a creative type across inventory segments | Apply to ad units and line items. Controls frequency of specific ad categories on portions of inventory (e.g., limit gambling ads to 2 per session on sports pages) |
| `AD_EXCLUSION` | Blocks ads from serving on inventory tagged with the exclusion label | Apply to line items (to be blocked) and ad units (blocking targets). When an ad request includes an exclusion label, line items with that label are excluded |
| `CREATIVE_WRAPPER` | Forces header/footer creatives to wrap around delivered ads | Apply to ad units or placements. Creative wrappers must be created separately and associated with the label |
| `CANONICAL_CATEGORY` | Maps label to a Google canonical ad category for cross-system blocking | Used for programmatic and Google Ads exclusions. Requires `adCategory` field to specify the Google ad category |
| `UNKNOWN` | Reserved for values not exposed by the API version | Should not be used when creating labels |

**Label Type Behavior:**

**COMPETITIVE_EXCLUSION:**
- Applies at the page level
- If two line items have the same competitive exclusion label, only one serves per page
- "Allow same advertiser exception" can be set in UI to permit same-advertiser competition
- Labels on line items inherit to the order level

**AD_UNIT_FREQUENCY_CAP:**
- Works in conjunction with frequency cap settings
- Applies to the portion of inventory with the label
- Stacks with line item-level frequency caps

**AD_EXCLUSION:**
- Two-step process: label the inventory, label the line items to exclude
- Ad request tags must pass the exclusion labels for blocking to occur
- Can be negated using `isNegated` in AppliedLabel

---

### AdCategoryDto Object

Used with CANONICAL_CATEGORY label type to map to Google's canonical ad categories.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `xsd:long` | Yes | Canonical ID of the Google ad category |
| `displayName` | `xsd:string` | - | Localized name of the category (read-only) |
| `parentId` | `xsd:long` | - | ID of the parent category, or 0 if top-level (read-only) |

**Usage:**
```python
# Create a label mapped to a Google ad category
label = {
    'name': 'Alcohol Ads',
    'types': ['CANONICAL_CATEGORY'],
    'adCategory': {
        'id': 12345  # Google canonical category ID for Alcohol
    }
}
```

---

### AppliedLabel Object

Represents a label applied to an entity (line item, ad unit, order, etc.).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `labelId` | `xsd:long` | Yes | The ID of the Label to apply |
| `isNegated` | `xsd:boolean` | No | Set to `true` to negate an inherited label. Default: `false` |

**Usage on Entities:**

Entities like LineItem, Order, and AdUnit have these label-related fields:

| Field | Type | Description |
|-------|------|-------------|
| `appliedLabels` | `AppliedLabel[]` | Labels directly applied to this entity |
| `effectiveAppliedLabels` | `AppliedLabel[]` | Read-only. Includes inherited labels from parent entities |

**Negating Inherited Labels:**
```python
# Line item inherits labels from order, but we want to exclude one
line_item = {
    'name': 'Special Promo Line Item',
    # ... other fields ...
    'appliedLabels': [
        {
            'labelId': 12345,  # The inherited label to negate
            'isNegated': True
        }
    ]
}
```

---

### LabelAction Types

| Action Type | Description |
|-------------|-------------|
| `ActivateLabels` | Enables deactivated labels, making them available for use |
| `DeactivateLabels` | Disables labels. Deactivated labels cannot be newly applied but remain on existing entities |

**Important Notes:**
- Deactivating a label does not remove it from entities already using it
- Deactivated labels are excluded from dropdowns in the UI
- Reactivating restores full functionality

---

### PQL Filtering for Labels

**Filterable Fields:**

| PQL Property | Maps To | Operators Supported |
|--------------|---------|---------------------|
| `id` | `Label.id` | `=`, `!=`, `IN` |
| `type` | `Label.types` | `=` |
| `name` | `Label.name` | `=`, `!=`, `LIKE` |
| `description` | `Label.description` | `=`, `LIKE` |
| `isActive` | `Label.isActive` | `=` |

**Query Examples:**

```python
# Get all active competitive exclusion labels
"isActive = true AND type = 'COMPETITIVE_EXCLUSION'"

# Get labels by name pattern
"name LIKE 'Brand_%'"

# Get multiple labels by ID
"id IN (123, 456, 789)"

# Get inactive labels for cleanup
"isActive = false"
```

---

## CustomFieldService

**WSDL:** `https://ads.google.com/apis/ads/publisher/v202511/CustomFieldService?wsdl`

Provides operations for creating and managing CustomField objects. Custom fields add user-defined metadata to orders, line items, creatives, and proposals.

### CustomFieldService Methods

#### createCustomFields

Creates new CustomField objects.

```
createCustomFields(customFields: CustomField[] | DropDownCustomField[]) -> CustomField[] | DropDownCustomField[]
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `customFields` | `CustomField[]` or `DropDownCustomField[]` | Yes | Array of custom fields to create |

**Required Fields for Creation:**
- `name` - Field name (max 127 characters)
- `entityType` - Type of entity this field applies to
- `dataType` - Type of data stored in this field
- `visibility` - UI visibility setting

**Returns:** Created custom fields with server-assigned `id` values

**Example:**
```python
# Create a text custom field for line items
custom_field = {
    'name': 'IO Number',
    'description': 'Internal insertion order reference number',
    'entityType': 'LINE_ITEM',
    'dataType': 'STRING',
    'visibility': 'FULL'
}

result = custom_field_service.createCustomFields([custom_field])
print(f"Created custom field ID: {result[0]['id']}")
```

---

#### createCustomFieldOptions

Creates new options for DROP_DOWN type custom fields.

```
createCustomFieldOptions(customFieldOptions: CustomFieldOption[]) -> CustomFieldOption[]
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `customFieldOptions` | `CustomFieldOption[]` | Yes | Array of options to create |

**Required Fields:**
- `customFieldId` - ID of the DROP_DOWN custom field
- `displayName` - Text shown in the dropdown

**Returns:** Created options with server-assigned `id` values

**Example:**
```python
# Add options to a dropdown custom field
options = [
    {'customFieldId': 12345, 'displayName': 'High Priority'},
    {'customFieldId': 12345, 'displayName': 'Medium Priority'},
    {'customFieldId': 12345, 'displayName': 'Low Priority'}
]

result = custom_field_service.createCustomFieldOptions(options)
for opt in result:
    print(f"Option '{opt['displayName']}' ID: {opt['id']}")
```

---

#### getCustomFieldsByStatement

Retrieves CustomField objects matching a PQL query.

```
getCustomFieldsByStatement(filterStatement: Statement) -> CustomFieldPage
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `filterStatement` | `Statement` | Yes | PQL query with optional pagination |

**Returns:** `CustomFieldPage` - Contains `results` array and `totalResultSetSize`

**Example:**
```python
# Get all active custom fields for line items
statement = ad_manager.StatementBuilder(version='v202511')
statement.Where("entityType = 'LINE_ITEM' AND isActive = true")
statement.OrderBy('name', ascending=True)

response = custom_field_service.getCustomFieldsByStatement(statement.ToStatement())
for field in response['results']:
    print(f"Field: {field['name']} (Type: {field['dataType']})")
```

---

#### getCustomFieldOption

Retrieves a specific CustomFieldOption by ID.

```
getCustomFieldOption(customFieldOptionId: long) -> CustomFieldOption
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `customFieldOptionId` | `xsd:long` | Yes | ID of the option to retrieve |

**Returns:** `CustomFieldOption` - The requested option

**Example:**
```python
option = custom_field_service.getCustomFieldOption(67890)
print(f"Option: {option['displayName']}")
```

---

#### updateCustomFields

Updates existing CustomField objects.

```
updateCustomFields(customFields: CustomField[] | DropDownCustomField[]) -> CustomField[] | DropDownCustomField[]
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `customFields` | `CustomField[]` or `DropDownCustomField[]` | Yes | Fields to update |

**Updatable Fields:**
- `name`
- `description`
- `visibility`

**Read-Only After Values Exist:**
- `entityType` - Cannot change once CustomFieldValue records exist
- `dataType` - Cannot change once CustomFieldValue records exist

**Returns:** Updated custom field objects

---

#### updateCustomFieldOptions

Updates existing CustomFieldOption objects.

```
updateCustomFieldOptions(customFieldOptions: CustomFieldOption[]) -> CustomFieldOption[]
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `customFieldOptions` | `CustomFieldOption[]` | Yes | Options to update |

**Updatable Fields:**
- `displayName`

**Example:**
```python
# Rename a dropdown option
option = custom_field_service.getCustomFieldOption(67890)
option['displayName'] = 'Critical Priority'
updated = custom_field_service.updateCustomFieldOptions([option])
```

---

#### performCustomFieldAction

Performs bulk actions on CustomField objects.

```
performCustomFieldAction(customFieldAction: CustomFieldAction, filterStatement: Statement) -> UpdateResult
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `customFieldAction` | `CustomFieldAction` | Yes | Action to perform |
| `filterStatement` | `Statement` | Yes | PQL query selecting fields |

**Returns:** `UpdateResult` - Contains `numChanges` field

**Example:**
```python
# Deactivate unused custom fields
statement = ad_manager.StatementBuilder()
statement.Where("name LIKE 'Legacy%'")

action = {'xsi_type': 'DeactivateCustomFields'}
result = custom_field_service.performCustomFieldAction(action, statement.ToStatement())
```

---

### CustomField Object - Complete Field Reference

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `id` | `xsd:long` | - | Yes | Unique identifier assigned by Google |
| `name` | `xsd:string` | Yes | No | Field name. Max 127 characters. Must be unique per entityType |
| `description` | `xsd:string` | No | No | Optional description. Max 511 characters |
| `isActive` | `xsd:boolean` | - | Yes | Whether the field is active. Controlled via performCustomFieldAction |
| `entityType` | `CustomFieldEntityType` | Yes | Conditional | Entity type this field applies to. Read-only if any CustomFieldValue exists |
| `dataType` | `CustomFieldDataType` | Yes | Conditional | Data type of the field. Read-only if any CustomFieldValue exists |
| `visibility` | `CustomFieldVisibility` | Yes | No | How the field appears in the UI |

**Field Details:**

**name**
- Must be unique within the same `entityType`
- Different entity types can have fields with the same name
- Used as the display label in UI forms

**entityType**
- Determines which entities can have values for this field
- Cannot be changed once any entity has a value for this field
- Each custom field belongs to exactly one entity type

**dataType**
- Determines the value format and input UI
- Cannot be changed once any entity has a value for this field
- For DROP_DOWN, options must be created separately

**visibility**
- Controls both UI display and editability
- API_ONLY fields are hidden from UI but fully functional via API
- Can be changed at any time

---

### DropDownCustomField Object

Extended CustomField type for dropdown selections. Inherits all CustomField fields.

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `options` | `CustomFieldOption[]` | - | Yes | Array of available options. Populated after creation via createCustomFieldOptions |

**Creating a Dropdown Custom Field:**
```python
# Step 1: Create the custom field
dropdown_field = {
    'name': 'Campaign Priority',
    'description': 'Priority level for campaign scheduling',
    'entityType': 'LINE_ITEM',
    'dataType': 'DROP_DOWN',
    'visibility': 'FULL'
}
created = custom_field_service.createCustomFields([dropdown_field])
field_id = created[0]['id']

# Step 2: Create the options
options = [
    {'customFieldId': field_id, 'displayName': 'P1 - Critical'},
    {'customFieldId': field_id, 'displayName': 'P2 - High'},
    {'customFieldId': field_id, 'displayName': 'P3 - Normal'},
    {'customFieldId': field_id, 'displayName': 'P4 - Low'}
]
custom_field_service.createCustomFieldOptions(options)
```

---

### CustomFieldOption Object

Represents a selectable option for DROP_DOWN type custom fields.

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `id` | `xsd:long` | - | Yes | Unique identifier assigned by Google |
| `customFieldId` | `xsd:long` | Yes | No | ID of the parent DROP_DOWN custom field |
| `displayName` | `xsd:string` | Yes | No | Text displayed in the dropdown menu |

**Notes:**
- Options cannot be deleted, only updated
- Changing `displayName` updates all entities using that option
- The `id` is used when setting values via DropDownCustomFieldValue

---

### CustomFieldEntityType Enum - Complete Reference

| Value | Description | Supported Services |
|-------|-------------|-------------------|
| `LINE_ITEM` | Custom field for LineItem entities | LineItemService, ForecastService |
| `ORDER` | Custom field for Order entities | OrderService |
| `CREATIVE` | Custom field for Creative entities | CreativeService |
| `PROPOSAL` | Custom field for Proposal entities | ProposalService |
| `PROPOSAL_LINE_ITEM` | Custom field for ProposalLineItem entities | ProposalLineItemService |
| `UNKNOWN` | Reserved value not exposed by API version | - |

**Entity Type Considerations:**

**LINE_ITEM:**
- Most commonly used entity type
- Values accessible in line item reports
- Inherited by child creatives for reporting purposes

**ORDER:**
- Applied at the order level
- Values visible on all line items within the order
- Good for campaign-wide metadata

**CREATIVE:**
- Applied to individual creatives
- Useful for tracking creative versions, approval status

**PROPOSAL/PROPOSAL_LINE_ITEM:**
- Used in sales workflow
- Values can be copied to orders/line items on booking

---

### CustomFieldDataType Enum - Complete Reference

| Value | Description | Value Storage | UI Input |
|-------|-------------|---------------|----------|
| `STRING` | Text value | `TextValue` | Text input field. Max 255 characters |
| `NUMBER` | Numeric value | `NumberValue` | Number input field. Supports decimals |
| `TOGGLE` | Boolean value | `BooleanValue` | Checkbox. Values: `true`, `false`, or empty |
| `DROP_DOWN` | Selection from predefined options | `DropDownCustomFieldValue` with `customFieldOptionId` | Dropdown select menu |
| `UNKNOWN` | Reserved value not exposed by API version | - | - |

**Data Type Details:**

**STRING:**
- Maximum 255 characters
- No validation beyond length
- Good for freeform text like notes, reference codes

**NUMBER:**
- Stored as double-precision floating point
- No min/max validation
- Good for quantities, rates, scores

**TOGGLE:**
- Three states: checked (true), unchecked (false), not set (null)
- In reports, shows as "Yes", "No", or empty

**DROP_DOWN:**
- Requires separately created CustomFieldOption records
- Values stored as option IDs, not text
- Best for controlled vocabularies

---

### CustomFieldVisibility Enum - Complete Reference

| Value | UI Display | UI Editable | API Accessible | Use Case |
|-------|------------|-------------|----------------|----------|
| `API_ONLY` | Hidden | No | Yes | System/integration data not meant for manual entry |
| `READ_ONLY` | Visible | No | Yes | Display-only data populated by integrations |
| `FULL` | Visible | Yes | Yes | Standard user-editable custom fields |
| `UNKNOWN` | - | - | - | Reserved for API version compatibility |

**Visibility Use Cases:**

**API_ONLY:**
- External system IDs (CRM, billing system references)
- Automated workflow states
- Data that would confuse users if visible

**READ_ONLY:**
- Calculated or derived values
- Data from external systems users should see but not edit
- Audit trail information

**FULL:**
- User-entered metadata (IO numbers, campaign tags)
- Priority selections
- Notes and descriptions

---

### CustomFieldAction Types

| Action Type | Description |
|-------------|-------------|
| `ActivateCustomFields` | Enables deactivated custom fields |
| `DeactivateCustomFields` | Disables custom fields |

**Deactivation Behavior:**
- Deactivated fields are hidden from UI forms
- Existing values are preserved on entities
- Values cannot be set on new entities via UI (API still works)
- Reactivating restores full functionality

---

### PQL Filtering for Custom Fields

**Filterable Fields:**

| PQL Property | Maps To | Operators Supported |
|--------------|---------|---------------------|
| `id` | `CustomField.id` | `=`, `!=`, `IN` |
| `entityType` | `CustomField.entityType` | `=` |
| `name` | `CustomField.name` | `=`, `!=`, `LIKE` |
| `isActive` | `CustomField.isActive` | `=` |
| `visibility` | `CustomField.visibility` | `=` |

**Query Examples:**

```python
# Get all active line item custom fields
"entityType = 'LINE_ITEM' AND isActive = true"

# Get dropdown fields only
"dataType = 'DROP_DOWN'"

# Get fields by visibility
"visibility = 'FULL'"

# Get fields with specific name pattern
"name LIKE 'Campaign%'"
```

---

## CustomFieldValue Usage

Custom field values are set on entities like LineItem, Order, and Creative through their `customFieldValues` field.

### CustomFieldValue Object

Used for STRING, NUMBER, and TOGGLE data types.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `customFieldId` | `xsd:long` | Yes | ID of the CustomField this value belongs to |
| `value` | `Value` | Yes | The value, using appropriate Value subtype |

**Value Subtypes:**

| Data Type | Value Class | Example |
|-----------|-------------|---------|
| STRING | `TextValue` | `{'xsi_type': 'TextValue', 'value': 'IO-2024-001'}` |
| NUMBER | `NumberValue` | `{'xsi_type': 'NumberValue', 'value': 42.5}` |
| TOGGLE | `BooleanValue` | `{'xsi_type': 'BooleanValue', 'value': True}` |

### DropDownCustomFieldValue Object

Used specifically for DROP_DOWN data type custom fields.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `customFieldId` | `xsd:long` | Yes | ID of the DROP_DOWN CustomField |
| `customFieldOptionId` | `xsd:long` | Yes | ID of the selected CustomFieldOption |

### Setting Custom Field Values on Entities

**On LineItem:**

```python
line_item = {
    'name': 'My Line Item',
    'orderId': 12345,
    # ... other required fields ...
    'customFieldValues': [
        # String value
        {
            'xsi_type': 'CustomFieldValue',
            'customFieldId': 100,  # IO Number field
            'value': {'xsi_type': 'TextValue', 'value': 'IO-2024-001'}
        },
        # Number value
        {
            'xsi_type': 'CustomFieldValue',
            'customFieldId': 101,  # Priority Score field
            'value': {'xsi_type': 'NumberValue', 'value': 85}
        },
        # Toggle value
        {
            'xsi_type': 'CustomFieldValue',
            'customFieldId': 102,  # Requires Approval field
            'value': {'xsi_type': 'BooleanValue', 'value': True}
        },
        # Dropdown value
        {
            'xsi_type': 'DropDownCustomFieldValue',
            'customFieldId': 103,  # Priority Level field
            'customFieldOptionId': 501  # ID of "High Priority" option
        }
    ]
}
```

**On Order:**

```python
order = {
    'name': 'Q4 Campaign',
    'advertiserId': 67890,
    # ... other fields ...
    'customFieldValues': [
        {
            'xsi_type': 'CustomFieldValue',
            'customFieldId': 200,  # Agency Code field (ORDER type)
            'value': {'xsi_type': 'TextValue', 'value': 'AGY-001'}
        }
    ]
}
```

**Updating Custom Field Values:**

```python
# Retrieve the line item
statement = ad_manager.StatementBuilder()
statement.Where("id = :id").WithBindVariable('id', line_item_id)
line_item = line_item_service.getLineItemsByStatement(statement.ToStatement())['results'][0]

# Modify custom field value
for cfv in line_item.get('customFieldValues', []):
    if cfv['customFieldId'] == target_field_id:
        cfv['value']['value'] = 'NEW-IO-NUMBER'
        break

# Update the line item
line_item_service.updateLineItems([line_item])
```

---

## Label Application to Entities

Labels are applied to entities through the `appliedLabels` field.

### Applying Labels to Line Items

```python
line_item = {
    'name': 'Auto Brand A Campaign',
    'orderId': 12345,
    # ... other fields ...
    'appliedLabels': [
        {'labelId': 1001},  # Competitive exclusion label
        {'labelId': 1002}   # Frequency cap label
    ]
}

# Create or update
line_item_service.createLineItems([line_item])
```

### Applying Labels to Ad Units

```python
ad_unit = {
    'name': 'Sports Section',
    'parentId': root_ad_unit_id,
    'adUnitSizes': [...],
    'appliedLabels': [
        {'labelId': 2001},  # Ad exclusion label
        {'labelId': 2002}   # Frequency cap label
    ]
}

inventory_service.createAdUnits([ad_unit])
```

### Viewing Effective Labels

```python
# Get a line item with all effective labels
statement = ad_manager.StatementBuilder()
statement.Where("id = :id").WithBindVariable('id', line_item_id)
line_item = line_item_service.getLineItemsByStatement(statement.ToStatement())['results'][0]

print("Directly Applied Labels:")
for label in line_item.get('appliedLabels', []):
    print(f"  Label ID: {label['labelId']}, Negated: {label.get('isNegated', False)}")

print("Effective Labels (including inherited):")
for label in line_item.get('effectiveAppliedLabels', []):
    print(f"  Label ID: {label['labelId']}, Negated: {label.get('isNegated', False)}")
```

### Negating Inherited Labels

When a line item inherits a label from its order that you want to remove:

```python
# Line item inherits competitive exclusion from order, but this line item is okay to compete
line_item['appliedLabels'] = [
    {
        'labelId': inherited_label_id,
        'isNegated': True  # Negates the inherited label for this line item
    }
]
line_item_service.updateLineItems([line_item])
```

---

## Custom Fields in Reporting

Custom fields can be included in reports using the custom dimension framework.

### CUSTOM_DIMENSION in Reports

The `CUSTOM_DIMENSION` dimension allows breaking down report data by custom targeting keys marked as dimensions.

**Configuration:**
1. In Ad Manager UI, mark custom targeting keys as "Report on this key"
2. Include the key IDs in `ReportQuery.customDimensionKeyIds`
3. Add `CUSTOM_DIMENSION` to report dimensions

```python
report_query = {
    'dimensions': ['DATE', 'LINE_ITEM_ID', 'CUSTOM_DIMENSION'],
    'columns': ['AD_SERVER_IMPRESSIONS', 'AD_SERVER_CLICKS'],
    'dateRangeType': 'LAST_WEEK',
    'customDimensionKeyIds': [12345, 67890]  # Custom targeting key IDs
}
```

### Custom Field Values in PQL

While custom field values cannot be directly filtered in standard PQL, you can:

1. **Export entity data with custom fields:**
```python
pql = """
SELECT Id, Name, CustomFieldId, CustomFieldValue
FROM Line_Item
WHERE OrderId = 12345
"""
```

2. **Query custom field definitions:**
```python
pql = """
SELECT Id, Name, EntityType, DataType, IsActive
FROM Custom_Field
WHERE EntityType = 'LINE_ITEM'
"""
```

---

## Python Code Examples

### Complete Label Management Example

```python
from googleads import ad_manager

def manage_labels():
    """Complete example of label management operations."""

    client = ad_manager.AdManagerClient.LoadFromStorage('googleads.yaml')
    label_service = client.GetService('LabelService', version='v202511')

    # 1. Create competitive exclusion labels
    labels_to_create = [
        {
            'name': 'Auto - Luxury Brands',
            'description': 'Competitive exclusion for luxury auto brands',
            'types': ['COMPETITIVE_EXCLUSION']
        },
        {
            'name': 'Auto - Economy Brands',
            'description': 'Competitive exclusion for economy auto brands',
            'types': ['COMPETITIVE_EXCLUSION']
        },
        {
            'name': 'Finance - Banking',
            'description': 'Competitive exclusion for banking advertisers',
            'types': ['COMPETITIVE_EXCLUSION', 'AD_EXCLUSION']  # Multiple types
        }
    ]

    created_labels = label_service.createLabels(labels_to_create)
    print("Created labels:")
    for label in created_labels:
        print(f"  {label['name']} (ID: {label['id']})")

    # 2. Query existing labels
    statement = ad_manager.StatementBuilder(version='v202511')
    statement.Where("isActive = true AND type = 'COMPETITIVE_EXCLUSION'")
    statement.OrderBy('name', ascending=True)

    response = label_service.getLabelsByStatement(statement.ToStatement())
    print(f"\nFound {response['totalResultSetSize']} competitive exclusion labels")

    # 3. Update a label
    if created_labels:
        label_to_update = created_labels[0]
        label_to_update['description'] = 'Updated: ' + label_to_update.get('description', '')
        updated = label_service.updateLabels([label_to_update])
        print(f"\nUpdated label: {updated[0]['name']}")

    # 4. Deactivate labels matching a pattern
    deactivate_statement = ad_manager.StatementBuilder()
    deactivate_statement.Where("name LIKE 'Deprecated%'")

    action = {'xsi_type': 'DeactivateLabels'}
    result = label_service.performLabelAction(action, deactivate_statement.ToStatement())
    print(f"\nDeactivated {result.get('numChanges', 0)} labels")

    return created_labels


def apply_labels_to_line_items(label_id, line_item_ids):
    """Apply a label to multiple line items."""

    client = ad_manager.AdManagerClient.LoadFromStorage('googleads.yaml')
    line_item_service = client.GetService('LineItemService', version='v202511')

    # Get the line items
    statement = ad_manager.StatementBuilder(version='v202511')
    statement.Where("id IN (:ids)").WithBindVariable('ids', line_item_ids)

    response = line_item_service.getLineItemsByStatement(statement.ToStatement())

    if not response.get('results'):
        print("No line items found")
        return

    # Add label to each line item
    for line_item in response['results']:
        existing_labels = line_item.get('appliedLabels', [])

        # Check if label already applied
        if not any(l['labelId'] == label_id for l in existing_labels):
            existing_labels.append({'labelId': label_id})
            line_item['appliedLabels'] = existing_labels

    # Update all line items
    updated = line_item_service.updateLineItems(response['results'])
    print(f"Applied label to {len(updated)} line items")


if __name__ == '__main__':
    manage_labels()
```

### Complete Custom Field Management Example

```python
from googleads import ad_manager

def manage_custom_fields():
    """Complete example of custom field management."""

    client = ad_manager.AdManagerClient.LoadFromStorage('googleads.yaml')
    custom_field_service = client.GetService('CustomFieldService', version='v202511')

    # 1. Create different types of custom fields
    fields_to_create = [
        # String field
        {
            'name': 'IO Number',
            'description': 'Insertion order reference number',
            'entityType': 'LINE_ITEM',
            'dataType': 'STRING',
            'visibility': 'FULL'
        },
        # Number field
        {
            'name': 'Budget Score',
            'description': 'Internal budget priority score (0-100)',
            'entityType': 'LINE_ITEM',
            'dataType': 'NUMBER',
            'visibility': 'FULL'
        },
        # Toggle field
        {
            'name': 'Requires Approval',
            'description': 'Whether line item needs manager approval',
            'entityType': 'LINE_ITEM',
            'dataType': 'TOGGLE',
            'visibility': 'FULL'
        },
        # Dropdown field
        {
            'name': 'Campaign Priority',
            'description': 'Priority level for campaign scheduling',
            'entityType': 'LINE_ITEM',
            'dataType': 'DROP_DOWN',
            'visibility': 'FULL'
        },
        # API-only field (hidden from UI)
        {
            'name': 'External System ID',
            'description': 'Reference ID from external system',
            'entityType': 'LINE_ITEM',
            'dataType': 'STRING',
            'visibility': 'API_ONLY'
        }
    ]

    created_fields = custom_field_service.createCustomFields(fields_to_create)
    print("Created custom fields:")
    for field in created_fields:
        print(f"  {field['name']} ({field['dataType']}) - ID: {field['id']}")

    # 2. Add options to the dropdown field
    dropdown_field = next((f for f in created_fields if f['dataType'] == 'DROP_DOWN'), None)

    if dropdown_field:
        options = [
            {'customFieldId': dropdown_field['id'], 'displayName': 'P1 - Critical'},
            {'customFieldId': dropdown_field['id'], 'displayName': 'P2 - High'},
            {'customFieldId': dropdown_field['id'], 'displayName': 'P3 - Normal'},
            {'customFieldId': dropdown_field['id'], 'displayName': 'P4 - Low'},
            {'customFieldId': dropdown_field['id'], 'displayName': 'P5 - Backlog'}
        ]

        created_options = custom_field_service.createCustomFieldOptions(options)
        print(f"\nCreated {len(created_options)} options for '{dropdown_field['name']}':")
        for opt in created_options:
            print(f"  {opt['displayName']} (ID: {opt['id']})")

    # 3. Query custom fields
    statement = ad_manager.StatementBuilder(version='v202511')
    statement.Where("entityType = 'LINE_ITEM' AND isActive = true")

    response = custom_field_service.getCustomFieldsByStatement(statement.ToStatement())
    print(f"\nTotal LINE_ITEM custom fields: {response['totalResultSetSize']}")

    return created_fields


def set_custom_field_values(line_item_id, custom_field_values):
    """Set custom field values on a line item.

    Args:
        line_item_id: The line item ID to update
        custom_field_values: Dict mapping field IDs to values, e.g.:
            {
                100: 'IO-2024-001',           # String
                101: 85.5,                     # Number
                102: True,                     # Toggle
                103: 501                       # Dropdown option ID
            }
    """

    client = ad_manager.AdManagerClient.LoadFromStorage('googleads.yaml')
    line_item_service = client.GetService('LineItemService', version='v202511')
    custom_field_service = client.GetService('CustomFieldService', version='v202511')

    # Get custom field definitions to determine types
    field_ids = list(custom_field_values.keys())
    statement = ad_manager.StatementBuilder(version='v202511')
    statement.Where("id IN (:ids)").WithBindVariable('ids', field_ids)

    field_response = custom_field_service.getCustomFieldsByStatement(statement.ToStatement())
    field_types = {f['id']: f['dataType'] for f in field_response.get('results', [])}

    # Get the line item
    li_statement = ad_manager.StatementBuilder(version='v202511')
    li_statement.Where("id = :id").WithBindVariable('id', line_item_id)

    li_response = line_item_service.getLineItemsByStatement(li_statement.ToStatement())

    if not li_response.get('results'):
        raise ValueError(f"Line item {line_item_id} not found")

    line_item = li_response['results'][0]

    # Build custom field values
    cfv_list = []
    for field_id, value in custom_field_values.items():
        data_type = field_types.get(field_id)

        if data_type == 'DROP_DOWN':
            cfv_list.append({
                'xsi_type': 'DropDownCustomFieldValue',
                'customFieldId': field_id,
                'customFieldOptionId': value
            })
        elif data_type == 'STRING':
            cfv_list.append({
                'xsi_type': 'CustomFieldValue',
                'customFieldId': field_id,
                'value': {'xsi_type': 'TextValue', 'value': str(value)}
            })
        elif data_type == 'NUMBER':
            cfv_list.append({
                'xsi_type': 'CustomFieldValue',
                'customFieldId': field_id,
                'value': {'xsi_type': 'NumberValue', 'value': float(value)}
            })
        elif data_type == 'TOGGLE':
            cfv_list.append({
                'xsi_type': 'CustomFieldValue',
                'customFieldId': field_id,
                'value': {'xsi_type': 'BooleanValue', 'value': bool(value)}
            })

    line_item['customFieldValues'] = cfv_list

    # Update
    updated = line_item_service.updateLineItems([line_item])
    print(f"Updated line item {line_item_id} with {len(cfv_list)} custom field values")

    return updated[0]


def query_line_items_by_custom_field(custom_field_id, option_id):
    """Find line items with a specific dropdown custom field value.

    Note: This requires iterating through line items as custom field values
    cannot be directly filtered in PQL.
    """

    client = ad_manager.AdManagerClient.LoadFromStorage('googleads.yaml')
    line_item_service = client.GetService('LineItemService', version='v202511')

    statement = ad_manager.StatementBuilder(version='v202511')
    statement.Limit(500)

    matching_line_items = []
    offset = 0

    while True:
        statement.Offset(offset)
        response = line_item_service.getLineItemsByStatement(statement.ToStatement())

        if not response.get('results'):
            break

        for line_item in response['results']:
            for cfv in line_item.get('customFieldValues', []):
                if (cfv.get('customFieldId') == custom_field_id and
                    cfv.get('customFieldOptionId') == option_id):
                    matching_line_items.append(line_item)
                    break

        offset += len(response['results'])

        if offset >= response['totalResultSetSize']:
            break

    print(f"Found {len(matching_line_items)} line items with custom field value")
    return matching_line_items


if __name__ == '__main__':
    manage_custom_fields()
```

### Creating Labels for Common Use Cases

```python
from googleads import ad_manager

def create_competitive_exclusion_labels(categories):
    """Create competitive exclusion labels for advertiser categories.

    Args:
        categories: List of category names (e.g., ['Automotive', 'Finance', 'Telecom'])
    """

    client = ad_manager.AdManagerClient.LoadFromStorage('googleads.yaml')
    label_service = client.GetService('LabelService', version='v202511')

    labels = [
        {
            'name': f'Competitive - {category}',
            'description': f'Competitive exclusion for {category} advertisers',
            'types': ['COMPETITIVE_EXCLUSION']
        }
        for category in categories
    ]

    created = label_service.createLabels(labels)
    return {label['name']: label['id'] for label in created}


def create_frequency_cap_labels(segments):
    """Create frequency cap labels for inventory segments.

    Args:
        segments: Dict mapping segment names to descriptions
    """

    client = ad_manager.AdManagerClient.LoadFromStorage('googleads.yaml')
    label_service = client.GetService('LabelService', version='v202511')

    labels = [
        {
            'name': f'FreqCap - {name}',
            'description': desc,
            'types': ['AD_UNIT_FREQUENCY_CAP']
        }
        for name, desc in segments.items()
    ]

    created = label_service.createLabels(labels)
    return {label['name']: label['id'] for label in created}


def create_ad_exclusion_labels(exclusion_types):
    """Create ad exclusion labels for blocking specific ad types.

    Args:
        exclusion_types: List of exclusion type names
    """

    client = ad_manager.AdManagerClient.LoadFromStorage('googleads.yaml')
    label_service = client.GetService('LabelService', version='v202511')

    labels = [
        {
            'name': f'Exclude - {exc_type}',
            'description': f'Block {exc_type} ads on labeled inventory',
            'types': ['AD_EXCLUSION']
        }
        for exc_type in exclusion_types
    ]

    created = label_service.createLabels(labels)
    return {label['name']: label['id'] for label in created}


# Example usage
if __name__ == '__main__':
    # Create competitive exclusion labels for industries
    comp_labels = create_competitive_exclusion_labels([
        'Automotive', 'Finance', 'Telecom', 'Insurance', 'Travel'
    ])
    print("Competitive exclusion labels:", comp_labels)

    # Create frequency cap labels for inventory segments
    freq_labels = create_frequency_cap_labels({
        'Premium Content': 'Limit ad frequency on premium content',
        'Video Pre-roll': 'Limit pre-roll ad frequency',
        'Homepage': 'Limit homepage ad exposure'
    })
    print("Frequency cap labels:", freq_labels)

    # Create ad exclusion labels
    excl_labels = create_ad_exclusion_labels([
        'Gambling', 'Alcohol', 'Political', 'Sensitive'
    ])
    print("Ad exclusion labels:", excl_labels)
```

---

## Best Practices

### Label Best Practices

1. **Naming Conventions**
   - Use prefixes to group related labels: `Competitive - `, `FreqCap - `, `Exclude - `
   - Include the label type in the name for clarity
   - Keep names concise but descriptive

2. **Label Type Selection**
   - Use COMPETITIVE_EXCLUSION for same-page brand protection
   - Use AD_UNIT_FREQUENCY_CAP for inventory-specific frequency limits
   - Use AD_EXCLUSION for blocking specific ad categories from inventory
   - Use CREATIVE_WRAPPER sparingly; it affects ad rendering

3. **Label Organization**
   - Create a consistent taxonomy before implementation
   - Document label purposes and application rules
   - Review labels periodically for cleanup opportunities

4. **Performance Considerations**
   - Minimize the number of labels per entity
   - Competitive exclusion checks happen at ad selection time
   - Too many labels can impact ad server performance

### Custom Field Best Practices

1. **Field Planning**
   - Define all required fields before creating line items
   - Consider which entity type each field belongs to
   - Plan for reporting needs when choosing data types

2. **Data Type Selection**
   - Use STRING for freeform text and external IDs
   - Use NUMBER for values that may need calculations
   - Use TOGGLE for yes/no flags
   - Use DROP_DOWN for controlled vocabularies

3. **Visibility Strategy**
   - Use API_ONLY for system integration data
   - Use READ_ONLY for derived/calculated values
   - Use FULL for standard user-editable fields

4. **Dropdown Options**
   - Create all options before use in production
   - Use descriptive option names
   - Consider ordering (options display alphabetically)

5. **Maintenance**
   - Deactivate unused fields instead of leaving them active
   - Update descriptions when purposes change
   - Document custom field purposes externally

---

## Error Handling

### Common LabelService Errors

| Error | Cause | Resolution |
|-------|-------|------------|
| `LabelError.INVALID_PREFIX` | Label name uses reserved prefix | Choose a different name prefix |
| `LabelError.DUPLICATE_NAME` | Label name already exists | Use unique name or find existing label |
| `UniqueError` | Attempting to create duplicate | Query for existing label first |
| `NotNullError.ARG1_NULL` | Required field is null | Ensure name and types are provided |
| `CollectionSizeError` | Too many labels in request | Batch into smaller requests |

### Common CustomFieldService Errors

| Error | Cause | Resolution |
|-------|-------|------------|
| `UniqueError` | Duplicate field name for entity type | Use unique name or find existing field |
| `NotNullError` | Required field missing | Provide name, entityType, dataType, visibility |
| `TypeError.INVALID_TYPE` | Wrong value type for field | Match value type to dataType |
| `ReadOnlyError` | Trying to change read-only field | entityType/dataType locked after values exist |

### Error Handling Pattern

```python
from googleads import ad_manager
from googleads.errors import GoogleAdsServerFault

def safe_create_labels(labels):
    """Create labels with error handling."""

    client = ad_manager.AdManagerClient.LoadFromStorage('googleads.yaml')
    label_service = client.GetService('LabelService', version='v202511')

    try:
        result = label_service.createLabels(labels)
        return result

    except GoogleAdsServerFault as e:
        for error in e.errors:
            error_type = error.get('errorString', 'Unknown')

            if 'DUPLICATE_NAME' in error_type:
                # Label already exists, try to find it
                existing = find_labels_by_name([l['name'] for l in labels])
                return existing

            elif 'INVALID_PREFIX' in error_type:
                print(f"Invalid label name prefix: {error}")
                raise

            else:
                print(f"Label creation error: {error}")
                raise

    except Exception as e:
        print(f"Unexpected error: {e}")
        raise


def find_labels_by_name(names):
    """Find existing labels by name."""

    client = ad_manager.AdManagerClient.LoadFromStorage('googleads.yaml')
    label_service = client.GetService('LabelService', version='v202511')

    statement = ad_manager.StatementBuilder(version='v202511')
    statement.Where("name IN (:names)").WithBindVariable('names', names)

    response = label_service.getLabelsByStatement(statement.ToStatement())
    return response.get('results', [])
```

---

## Troubleshooting

### Labels Not Applying

**Symptom:** Labels added to line items but competitive exclusion not working.

**Possible Causes:**
1. Label type is not COMPETITIVE_EXCLUSION
2. Labels are deactivated
3. "Allow same advertiser exception" is enabled

**Resolution:**
```python
# Verify label type and status
statement = ad_manager.StatementBuilder()
statement.Where("id = :id").WithBindVariable('id', label_id)

label = label_service.getLabelsByStatement(statement.ToStatement())['results'][0]
print(f"Label types: {label['types']}")
print(f"Is active: {label['isActive']}")
```

### Custom Field Values Not Saving

**Symptom:** Custom field values disappear after save.

**Possible Causes:**
1. Wrong value type for the data type
2. Custom field ID is incorrect
3. Custom field is for wrong entity type

**Resolution:**
```python
# Verify custom field exists and matches entity type
statement = ad_manager.StatementBuilder()
statement.Where("id = :id").WithBindVariable('id', custom_field_id)

field = custom_field_service.getCustomFieldsByStatement(statement.ToStatement())['results'][0]
print(f"Entity type: {field['entityType']}")
print(f"Data type: {field['dataType']}")
print(f"Is active: {field['isActive']}")
```

### Dropdown Options Missing

**Symptom:** Cannot select dropdown values; options appear empty.

**Possible Causes:**
1. Options not created for the custom field
2. Custom field is not DROP_DOWN type
3. Viewing wrong entity type in UI

**Resolution:**
```python
# List all options for a dropdown field
statement = ad_manager.StatementBuilder()
statement.Where("id = :id").WithBindVariable('id', dropdown_field_id)

field = custom_field_service.getCustomFieldsByStatement(statement.ToStatement())['results'][0]

if 'options' in field:
    print("Dropdown options:")
    for opt in field['options']:
        print(f"  {opt['displayName']} (ID: {opt['id']})")
else:
    print("No options found - create them with createCustomFieldOptions")
```

### Cannot Change Entity Type or Data Type

**Symptom:** Error when trying to update entityType or dataType.

**Cause:** These fields become read-only once any entity has a CustomFieldValue for this field.

**Resolution:**
1. Create a new custom field with the desired type
2. Migrate values from old field to new field
3. Deactivate the old field

```python
# Check if field has values (cannot be directly queried)
# Instead, try updating and catch the error

try:
    field['entityType'] = 'ORDER'  # Try to change
    custom_field_service.updateCustomFields([field])
except GoogleAdsServerFault as e:
    if 'READ_ONLY' in str(e):
        print("Field has values and cannot be modified. Create a new field instead.")
```

---

## Related Documentation

- [LineItemService](../orders-line-items/README.md) - Applying labels and custom fields to line items
- [OrderService](../orders-line-items/README.md) - Custom fields on orders
- [AdUnitService](../inventory/README.md) - Applying labels to ad units
- [ReportService](../reporting/README.md) - Custom dimensions in reports

---

## API Reference Links

- [LabelService v202511](https://developers.google.com/ad-manager/api/reference/v202511/LabelService)
- [CustomFieldService v202511](https://developers.google.com/ad-manager/api/reference/v202511/CustomFieldService)
- [Label Type Reference](https://developers.google.com/ad-manager/api/reference/v202511/LabelService.LabelType)
- [CustomField Type Reference](https://developers.google.com/ad-manager/api/reference/v202511/CustomFieldService.CustomField)
