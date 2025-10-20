# IzzyMart Self Checkout GUI

A Vue 3 touchscreen-friendly self-checkout interface for IzzyMart.

## Features

- **Barcode Scanner Support**: Automatically detects HID barcode scanner input
- **Touch-Friendly Interface**: Large buttons and controls optimized for touchscreens
- **Product Display**: Shows detailed product information including images, nutrition, and allergens
- **Shopping Cart**: Real-time cart management with add/remove functionality
- **On-Screen Keyboard**: Built-in keyboard for product search
- **Product Search**: Search products by name
- **Responsive Layout**: 2/3 product details, 1/3 shopping cart

## Tech Stack

- **Vue 3** with Composition API and TypeScript
- **Vuetify 3** for Material Design components
- **Pinia** for state management
- **Vue Router** for navigation
- **Axios** for API communication

## Prerequisites

- Node.js 14+ and npm
- IzzyMart API running on http://localhost:8000

## Installation

```bash
cd gui
npm install
```

## Development

```bash
npm run serve
```

The app will be available at http://localhost:8080

## Build for Production

```bash
npm run build
```

## Usage

### Barcode Scanner

The app automatically detects barcode scanner input when:
- No input fields are focused
- Number keys are pressed rapidly (within 100ms between keystrokes)
- Minimum 8 digits are scanned

### Product Search

1. Click "Search Products" button
2. Use the on-screen keyboard to type product name
3. Results appear automatically as you type
4. Click on a product to add it to cart

### Shopping Cart

- **Add More**: Click the "+" button next to items
- **Remove One**: Click the "-" button next to items
- **Delete Item**: Click the trash icon to remove completely
- **Clear Cart**: Use the "Clear Cart" button on the left panel

## Project Structure

```
gui/
├── public/              # Static assets
├── src/
│   ├── components/      # Vue components
│   │   ├── CartList.vue          # Shopping cart display
│   │   ├── ItemDetails.vue       # Product details panel
│   │   ├── OnScreenKeyboard.vue  # Touch keyboard
│   │   ├── ScannerInput.vue      # Barcode scanner handler
│   │   └── SearchDialog.vue      # Product search modal
│   ├── plugins/         # Vuetify configuration
│   ├── router/          # Vue Router setup
│   ├── services/        # API services
│   │   └── api.ts                # API client
│   ├── store/           # Pinia stores
│   │   └── cart.ts               # Shopping cart state
│   ├── types/           # TypeScript type definitions
│   ├── views/           # Page components
│   │   └── CheckoutView.vue      # Main checkout page
│   ├── App.vue          # Root component
│   └── main.ts          # App entry point
├── .env                 # Environment variables
├── package.json         # Dependencies
└── vue.config.js        # Vue CLI configuration
```

## API Integration

The GUI connects to the IzzyMart API with the following endpoints:

- `POST /auth/token` - Authentication
- `GET /products/upc/:upc` - Get product by UPC
- `GET /products` - List all products (for search)
- `GET /files/:id/image` - Get product images

Configure the API URL in `.env`:

```
VUE_APP_API_URL=http://localhost:8000/api/v1
```

## Configuration

Default credentials (can be changed in `.env`):
- Username: `root`
- Password: `root`

## Touchscreen Optimization

The interface is optimized for touchscreens with:
- Minimum button size of 60x60px
- Large, easy-to-tap controls
- No hover-dependent interactions
- On-screen keyboard for text input
- Clear visual feedback for all actions

## License

Proprietary - IzzyMart
