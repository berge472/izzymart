# Debug Mode - URL Parameters

The IzzyMart GUI supports URL parameters to control application behavior during development and testing.

## Debug Mode

Enable debug mode by adding `?debug=true` to the URL:

```
http://localhost:8080/?debug=true
```

### What Debug Mode Does

When debug mode is enabled:

1. **Disables API Caching**: All UPC/barcode lookups bypass the database cache and perform fresh lookups
   - Product lookups always fetch from external APIs (OpenFoodFacts, Amazon, etc.)
   - Useful for testing product data updates without clearing the database
   - Helps verify that API integrations are working correctly

2. **Console Logging**: Extra debug information is logged to the browser console
   - Shows whether cache is enabled or disabled for each request
   - Displays the current debug mode state

### Supported URL Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `debug` | `true`, `1`, `yes` | `false` | Enables debug mode (case insensitive) |

### Examples

**Normal Mode (with caching):**
```
http://localhost:8080/
```

**Debug Mode (without caching):**
```
http://localhost:8080/?debug=true
http://localhost:8080/?debug=1
http://localhost:8080/?debug=yes
```

**Admin View with Debug Mode:**
```
http://localhost:8080/admin?debug=true
```

### Implementation Details

The debug parameter is read from the URL using the `isDebugMode()` utility function from `/src/utils/urlParams.ts`.

Components that make UPC lookups check this parameter and pass `cache=false` to the API when debug mode is enabled:

- **ScannerInput.vue** - Barcode scanning for adding items to cart
- **AdminView.vue** - Admin product editing interface

### Use Cases

1. **Testing Product Updates**: When you update product data in external APIs, use debug mode to see the changes immediately without clearing your local database

2. **API Integration Testing**: Verify that OpenFoodFacts and Amazon integrations are working correctly by forcing fresh lookups

3. **Troubleshooting**: When a product seems to have outdated information, use debug mode to fetch the latest data

4. **Development**: During development of new features, keep debug mode enabled to always work with fresh data
