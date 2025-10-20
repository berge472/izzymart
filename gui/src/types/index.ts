export interface Product {
  id?: string
  product_type?: string
  upc: string
  name: string
  brand?: string
  price?: number
  price_source?: string
  image_url?: string
  images?: string[]
  image_source?: string
  description?: string
  nutrition?: NutritionInfo
  ingredients?: string
  allergens?: string[]
  tags?: string[]
  metadata?: Record<string, any>
  // Book-specific fields
  isbn?: string
  author?: string
  publisher?: string
  publication_date?: string
  page_count?: number
  language?: string
  categories?: string[]
}

export interface NutritionInfo {
  serving_size?: string
  calories?: number
  fat?: number
  saturated_fat?: number
  trans_fat?: number
  cholesterol?: number
  sodium?: number
  carbohydrates?: number
  fiber?: number
  sugars?: number
  protein?: number
  nutrition_grade?: string
}

export interface CartItem {
  product: Product
  quantity: number
  timestamp: number
}

export interface AuthTokenResponse {
  access_token: string
  token_type: string
}
