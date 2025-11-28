# NativeStyleService - Google Ad Manager SOAP API v202511

## Overview

The `NativeStyleService` provides methods for creating, retrieving, updating, and managing **NativeStyle** objects in Google Ad Manager. Native styles define the look and feel of native ads for both web and mobile app inventory.

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Native Style** | Defines HTML/CSS rendering for native ad creatives |
| **Creative Template** | The native ad format (variables like headline, image, body) that the style renders |
| **Fluid Size** | Responsive sizing using 1x1 pixel dimensions with `isFluid=true` |
| **Fixed Size** | Specific dimensions for the rendered native ad |

### Service Endpoint

| Property | Value |
|----------|-------|
| **WSDL** | `https://ads.google.com/apis/ads/publisher/v202511/NativeStyleService?wsdl` |
| **Namespace** | `https://www.google.com/apis/ads/publisher/v202511` |

---

## Service Methods

### createNativeStyles

Creates new NativeStyle objects.

```
NativeStyle[] createNativeStyles(NativeStyle[] nativeStyles)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `nativeStyles` | `NativeStyle[]` | Array of NativeStyle objects to create |

**Returns:** `NativeStyle[]` - The created native styles with assigned IDs

---

### getNativeStylesByStatement

Retrieves NativeStyle objects matching specified filter criteria.

```
NativeStylePage getNativeStylesByStatement(Statement filterStatement)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `filterStatement` | `Statement` | PQL statement for filtering |

**Returns:** `NativeStylePage` - Page of matching native styles

**Filterable Fields:**

| Field | Type | Operators |
|-------|------|-----------|
| `id` | `xsd:long` | `=`, `!=`, `IN`, `NOT IN` |
| `name` | `xsd:string` | `=`, `!=`, `LIKE` |

---

### updateNativeStyles

Updates existing NativeStyle objects.

```
NativeStyle[] updateNativeStyles(NativeStyle[] nativeStyles)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `nativeStyles` | `NativeStyle[]` | Array of NativeStyle objects to update |

**Returns:** `NativeStyle[]` - The updated native styles

**Note:** The `creativeTemplateId` cannot be changed after creation.

---

### performNativeStyleAction

Performs bulk actions on NativeStyle objects matching filter criteria.

```
UpdateResult performNativeStyleAction(NativeStyleAction action, Statement filterStatement)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `action` | `NativeStyleAction` | The action to perform |
| `filterStatement` | `Statement` | PQL statement to select target styles |

**Returns:** `UpdateResult` - Number of objects affected

---

## Data Models

### NativeStyle Object

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `id` | `xsd:long` | — | ✅ | Unique identifier assigned by Google |
| `name` | `xsd:string` | ✅ | — | Name of the native style (max 255 characters) |
| `htmlSnippet` | `xsd:string` | ✅ | — | HTML markup with placeholders for variables |
| `cssSnippet` | `xsd:string` | ✅ | — | CSS styles with placeholders for variables |
| `creativeTemplateId` | `xsd:long` | ✅ (creation) | ✅ (after creation) | Associated native ad format template ID |
| `isFluid` | `xsd:boolean` | — | — | If `true`, uses fluid sizing (must use 1x1 size) |
| `targeting` | `Targeting` | — | — | Targeting criteria (only `inventoryTargeting` and `customTargeting` supported) |
| `status` | `NativeStyleStatus` | — | ✅ | Current status of the native style |
| `size` | `Size` | ✅ | — | Dimensions of the rendered native ad |

### Size Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `width` | `xsd:int` | ✅ | Width in pixels (use 1 for fluid) |
| `height` | `xsd:int` | ✅ | Height in pixels (use 1 for fluid) |
| `isAspectRatio` | `xsd:boolean` | — | Whether dimensions represent aspect ratio |

### NativeStylePage Object

| Field | Type | Description |
|-------|------|-------------|
| `totalResultSetSize` | `xsd:int` | Total number of matching results |
| `startIndex` | `xsd:int` | Starting index of this page |
| `results` | `NativeStyle[]` | Array of NativeStyle objects |

### UpdateResult Object

| Field | Type | Description |
|-------|------|-------------|
| `numChanges` | `xsd:int` | Number of objects affected by the action |

---

## Enumerations

### NativeStyleStatus

| Value | Description |
|-------|-------------|
| `ACTIVE` | The native style is active and can serve ads |
| `INACTIVE` | The native style is inactive and will not serve |
| `ARCHIVED` | The native style is archived |
| `UNKNOWN` | Value not available in the requested API version |

### NativeStyleAction Types

| Action | xsi:type | Description |
|--------|----------|-------------|
| **Activate** | `ActivateNativeStyles` | Activates native styles for serving |
| **Deactivate** | `DeactivateNativeStyles` | Deactivates native styles (stops serving) |
| **Archive** | `ArchiveNativeStyles` | Archives native styles |

---

## HTML/CSS Snippets

### Variable Placeholders

Native styles use placeholders that map to creative template variables. The placeholder syntax is:

```
%%VARIABLE_NAME%%
```

### Common System-Defined Variables

For system-defined native ad formats, common variables include:

| Variable | Description | Example Placeholder |
|----------|-------------|---------------------|
| `Headline` | Main headline text | `%%Headline%%` |
| `Body` | Body/description text | `%%Body%%` |
| `Image` | Main image URL | `%%Image%%` |
| `Logo` | Advertiser logo URL | `%%Logo%%` |
| `Calltoaction` | Call-to-action button text | `%%Calltoaction%%` |
| `Advertiser` | Advertiser name | `%%Advertiser%%` |
| `Price` | Product price | `%%Price%%` |
| `Starrating` | Star rating value | `%%Starrating%%` |
| `Store` | App store name | `%%Store%%` |
| `DeeplinkUrl` | Deep link URL | `%%DeeplinkUrl%%` |

### Common Macros

| Macro | Description |
|-------|-------------|
| `%%CLICK_URL_UNESC%%` | Unescaped click tracking URL |
| `%%CLICK_URL_ESC%%` | Escaped click tracking URL |
| `%%CACHEBUSTER%%` | Random number for cache busting |
| `%%ONE_CLICK_HANDLER_TARGET%%` | Universal link handler for native creatives |

### Example HTML Snippet

```html
<div class="native-ad">
  <div class="ad-image">
    <img src="%%Image%%" alt="%%Headline%%">
  </div>
  <div class="ad-content">
    <h2 class="ad-headline">%%Headline%%</h2>
    <p class="ad-body">%%Body%%</p>
    <div class="ad-meta">
      <img src="%%Logo%%" class="ad-logo" alt="%%Advertiser%%">
      <span class="ad-advertiser">%%Advertiser%%</span>
    </div>
    <a href="%%CLICK_URL_UNESC%%" class="ad-cta">%%Calltoaction%%</a>
  </div>
</div>
```

### Example CSS Snippet

```css
.native-ad {
  font-family: Arial, sans-serif;
  max-width: 400px;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
}

.ad-image img {
  width: 100%;
  height: auto;
}

.ad-content {
  padding: 16px;
}

.ad-headline {
  font-size: 18px;
  font-weight: bold;
  margin: 0 0 8px 0;
  color: #333;
}

.ad-body {
  font-size: 14px;
  color: #666;
  margin: 0 0 12px 0;
}

.ad-meta {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.ad-logo {
  width: 24px;
  height: 24px;
  margin-right: 8px;
}

.ad-advertiser {
  font-size: 12px;
  color: #999;
}

.ad-cta {
  display: inline-block;
  background: #1a73e8;
  color: white;
  padding: 10px 20px;
  border-radius: 4px;
  text-decoration: none;
}
```

---

## Python Code Examples

### Setup

```python
from googleads import ad_manager

# Initialize client
client = ad_manager.AdManagerClient.LoadFromStorage()
native_style_service = client.GetService('NativeStyleService', version='v202511')
```

### Create a Native Style

```python
def create_native_style(name, creative_template_id, width, height, html_snippet, css_snippet, is_fluid=False):
    """Create a new native style."""

    native_style = {
        'name': name,
        'creativeTemplateId': creative_template_id,
        'size': {
            'width': 1 if is_fluid else width,
            'height': 1 if is_fluid else height,
            'isAspectRatio': False
        },
        'htmlSnippet': html_snippet,
        'cssSnippet': css_snippet,
        'isFluid': is_fluid
    }

    result = native_style_service.createNativeStyles([native_style])

    for style in result:
        print(f"Created NativeStyle ID: {style['id']}, Name: {style['name']}")

    return result

# Example: Create a fluid native style for in-feed ads
html = '''
<div class="native-ad">
  <img src="%%Image%%" class="main-image">
  <h2>%%Headline%%</h2>
  <p>%%Body%%</p>
  <span class="sponsored">Sponsored by %%Advertiser%%</span>
</div>
'''

css = '''
.native-ad { font-family: sans-serif; padding: 16px; }
.main-image { width: 100%; border-radius: 8px; }
h2 { font-size: 18px; margin: 12px 0 8px; }
p { font-size: 14px; color: #666; }
.sponsored { font-size: 12px; color: #999; }
'''

# 10004400 is the system template ID for App Install ads
create_native_style(
    name='In-Feed Native Style',
    creative_template_id=10004400,
    width=300,
    height=250,
    html_snippet=html,
    css_snippet=css,
    is_fluid=True
)
```

### Query Native Styles

```python
def get_native_styles_by_name(name_pattern):
    """Get native styles matching a name pattern."""

    statement = (ad_manager.StatementBuilder(version='v202511')
                 .Where('name LIKE :name')
                 .WithBindVariable('name', f'%{name_pattern}%')
                 .Limit(100))

    result = native_style_service.getNativeStylesByStatement(statement.ToStatement())

    if 'results' in result:
        print(f"Found {result['totalResultSetSize']} native styles:")
        for style in result['results']:
            print(f"  ID: {style['id']}")
            print(f"  Name: {style['name']}")
            print(f"  Status: {style['status']}")
            print(f"  Template ID: {style['creativeTemplateId']}")
            print(f"  Size: {style['size']['width']}x{style['size']['height']}")
            print(f"  Is Fluid: {style.get('isFluid', False)}")
            print("---")
    else:
        print("No native styles found.")

    return result.get('results', [])

# Get all native styles containing "In-Feed" in the name
get_native_styles_by_name('In-Feed')
```

### Get All Active Native Styles

```python
def get_active_native_styles():
    """Get all active native styles with pagination."""

    statement = (ad_manager.StatementBuilder(version='v202511')
                 .Limit(500)
                 .Offset(0))

    all_styles = []

    while True:
        result = native_style_service.getNativeStylesByStatement(statement.ToStatement())

        if 'results' in result:
            # Filter for active styles
            active_styles = [s for s in result['results'] if s['status'] == 'ACTIVE']
            all_styles.extend(active_styles)

            statement.offset += statement.limit
            if statement.offset >= result['totalResultSetSize']:
                break
        else:
            break

    print(f"Found {len(all_styles)} active native styles")
    return all_styles
```

### Update a Native Style

```python
def update_native_style_html(style_id, new_html_snippet, new_css_snippet=None):
    """Update the HTML/CSS of an existing native style."""

    # First, fetch the existing style
    statement = (ad_manager.StatementBuilder(version='v202511')
                 .Where('id = :id')
                 .WithBindVariable('id', style_id))

    result = native_style_service.getNativeStylesByStatement(statement.ToStatement())

    if not result.get('results'):
        raise ValueError(f"Native style with ID {style_id} not found")

    style = result['results'][0]

    # Update the snippets
    style['htmlSnippet'] = new_html_snippet
    if new_css_snippet:
        style['cssSnippet'] = new_css_snippet

    # Save the update
    updated = native_style_service.updateNativeStyles([style])

    print(f"Updated NativeStyle ID: {updated[0]['id']}")
    return updated[0]
```

### Add Targeting to a Native Style

```python
def add_targeting_to_native_style(style_id, ad_unit_ids=None, custom_targeting_key_id=None, custom_targeting_value_ids=None):
    """Add inventory and/or custom targeting to a native style."""

    # Fetch existing style
    statement = (ad_manager.StatementBuilder(version='v202511')
                 .Where('id = :id')
                 .WithBindVariable('id', style_id))

    result = native_style_service.getNativeStylesByStatement(statement.ToStatement())

    if not result.get('results'):
        raise ValueError(f"Native style with ID {style_id} not found")

    style = result['results'][0]

    # Build targeting
    targeting = {}

    # Add inventory targeting
    if ad_unit_ids:
        targeting['inventoryTargeting'] = {
            'targetedAdUnits': [
                {'adUnitId': ad_unit_id, 'includeDescendants': True}
                for ad_unit_id in ad_unit_ids
            ]
        }

    # Add custom targeting
    if custom_targeting_key_id and custom_targeting_value_ids:
        targeting['customTargeting'] = {
            'logicalOperator': 'OR',
            'children': [{
                'xsi_type': 'CustomCriteria',
                'keyId': custom_targeting_key_id,
                'valueIds': custom_targeting_value_ids,
                'operator': 'IS'
            }]
        }

    style['targeting'] = targeting

    # Save the update
    updated = native_style_service.updateNativeStyles([style])

    print(f"Added targeting to NativeStyle ID: {updated[0]['id']}")
    return updated[0]
```

### Perform Actions on Native Styles

```python
def activate_native_styles(style_ids):
    """Activate one or more native styles."""

    statement = (ad_manager.StatementBuilder(version='v202511')
                 .Where('id IN (:ids)')
                 .WithBindVariable('ids', style_ids))

    action = {'xsi_type': 'ActivateNativeStyles'}

    result = native_style_service.performNativeStyleAction(action, statement.ToStatement())

    print(f"Activated {result['numChanges']} native styles")
    return result


def deactivate_native_styles(style_ids):
    """Deactivate one or more native styles."""

    statement = (ad_manager.StatementBuilder(version='v202511')
                 .Where('id IN (:ids)')
                 .WithBindVariable('ids', style_ids))

    action = {'xsi_type': 'DeactivateNativeStyles'}

    result = native_style_service.performNativeStyleAction(action, statement.ToStatement())

    print(f"Deactivated {result['numChanges']} native styles")
    return result


def archive_native_styles(style_ids):
    """Archive one or more native styles."""

    statement = (ad_manager.StatementBuilder(version='v202511')
                 .Where('id IN (:ids)')
                 .WithBindVariable('ids', style_ids))

    action = {'xsi_type': 'ArchiveNativeStyles'}

    result = native_style_service.performNativeStyleAction(action, statement.ToStatement())

    print(f"Archived {result['numChanges']} native styles")
    return result
```

---

## Common Creative Template IDs

System-defined native ad format template IDs:

| Template ID | Format Name | Description |
|-------------|-------------|-------------|
| `10004400` | App Install | Mobile app installation ads |
| `10004401` | Content | Content recommendation ads |
| `10004402` | Video App Install | Video-based app install ads |
| `10004403` | Video Content | Video content ads |

**Note:** Custom native ad formats have unique template IDs assigned when created.

---

## Targeting Limitations

Native styles support **only** these targeting types:

| Targeting Type | Supported |
|----------------|-----------|
| `inventoryTargeting` | ✅ Yes |
| `customTargeting` | ✅ Yes |
| `geoTargeting` | ❌ No |
| `technologyTargeting` | ❌ No |
| `dayPartTargeting` | ❌ No |
| All other targeting types | ❌ No |

---

## Error Handling

### NativeStyleError.Reason

| Error Reason | Description |
|--------------|-------------|
| `ACTIVE_CREATIVE_TEMPLATE_REQUIRED` | The creative template must be active |
| `INVALID_CUSTOM_TARGETING_MATCH_TYPE` | Invalid match type for custom targeting |
| `INVALID_INVENTORY_TARGETING_TYPE` | Targeting type not supported for native styles |
| `INVALID_STATUS` | Invalid status transition |
| `INVALID_TARGETING_TYPE` | Only inventory and custom targeting allowed |
| `NATIVE_CREATIVE_TEMPLATE_REQUIRED` | Template must be native-eligible |
| `TOO_MANY_CUSTOM_TARGETING_KEY_VALUES` | Exceeded maximum custom targeting values |
| `UNIQUE_SNIPPET_REQUIRED` | HTML and CSS snippets must be unique |
| `UNRECOGNIZED_MACRO` | Unknown macro/placeholder in snippet |
| `UNRECOGNIZED_PLACEHOLDER` | Unknown variable placeholder in snippet |
| `UNKNOWN` | Unknown error |

### Example Error Handling

```python
from googleads import errors

def create_native_style_with_error_handling(native_style):
    """Create native style with comprehensive error handling."""
    try:
        result = native_style_service.createNativeStyles([native_style])
        return result[0]

    except errors.GoogleAdsServerFault as e:
        for error in e.errors:
            error_type = error['ApiExceptionFault']['errors'][0]['@xsi:type']
            reason = error['ApiExceptionFault']['errors'][0].get('reason', 'Unknown')

            if 'NativeStyleError' in error_type:
                if reason == 'NATIVE_CREATIVE_TEMPLATE_REQUIRED':
                    print("Error: The template ID must be for a native-eligible template")
                elif reason == 'UNRECOGNIZED_PLACEHOLDER':
                    print("Error: Invalid variable placeholder in HTML/CSS snippet")
                elif reason == 'INVALID_TARGETING_TYPE':
                    print("Error: Only inventory and custom targeting are supported")
                else:
                    print(f"NativeStyleError: {reason}")
            else:
                print(f"API Error: {error_type} - {reason}")

        raise
```

---

## Best Practices

### HTML/CSS Snippets
1. **No validation** - The API does not validate HTML/CSS; test thoroughly in the UI
2. **Use responsive CSS** - Design for multiple screen sizes
3. **Escape special characters** - Properly escape quotes and special characters
4. **Keep snippets small** - Large snippets may impact ad load time

### Targeting
1. **Be specific** - Target to specific ad units for better control
2. **Use custom targeting** - Leverage key-value pairs for flexible targeting
3. **Test combinations** - Verify that targeting doesn't conflict

### Status Management
1. **Create as inactive** - Create styles in inactive state, then activate after testing
2. **Archive instead of delete** - Use archive to preserve history
3. **Batch operations** - Use performNativeStyleAction for bulk status changes

---

## Related Services

| Service | Purpose |
|---------|---------|
| `CreativeTemplateService` | Retrieve native ad format templates |
| `CreativeService` | Create native creatives using templates |
| `LineItemService` | Traffic line items with native creative placeholders |
| `InventoryService` | Get ad unit IDs for targeting |
| `CustomTargetingService` | Get custom targeting keys/values for targeting |

---

## Resources

- [NativeStyleService Reference (v202511)](https://developers.google.com/ad-manager/api/reference/v202511/NativeStyleService)
- [NativeStyle Type Reference](https://developers.google.com/ad-manager/api/reference/v202511/NativeStyleService.NativeStyle)
- [Native Ads API Guide](https://developers.google.com/ad-manager/api/native)
- [Style Your Native Ad (Help)](https://support.google.com/admanager/answer/7661907)
- [Add Code for Native Ads (Help)](https://support.google.com/admanager/answer/6366914)
- [Create Custom Native Ad Formats (Help)](https://support.google.com/admanager/answer/6366911)
