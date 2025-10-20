import axios from 'axios'
import type { Product, AuthTokenResponse } from '@/types'

const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:8000/api/v1'

class ApiService {
  private token: string | null = null

  async authenticate(username: string = 'root', password: string = 'root'): Promise<void> {
    const formData = new URLSearchParams()
    formData.append('username', username)
    formData.append('password', password)

    const response = await axios.post<AuthTokenResponse>(
      `${API_URL}/auth/token`,
      formData,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    )

    this.token = response.data.access_token
  }

  private getHeaders(required: boolean = true) {
    if (!this.token) {
      if (required) {
        throw new Error('Not authenticated')
      }
      return {}
    }
    return {
      'Authorization': `Bearer ${this.token}`
    }
  }

  async getProductByUPC(upc: string, cache: boolean = true): Promise<Product> {
    // UPC lookup doesn't require authentication
    const response = await axios.get<Product>(
      `${API_URL}/products/upc/${upc}?cache=${cache}`
    )
    return response.data
  }

  async searchProducts(query: string): Promise<Product[]> {
    try {
      // For now, we don't have a search endpoint, so this is a placeholder
      // You might want to add a search endpoint to your API
      const response = await axios.get<Product[]>(
        `${API_URL}/products`,
        { headers: this.getHeaders() }
      )

      // Filter locally by name
      const allProducts = response.data
      const lowerQuery = query.toLowerCase()
      return allProducts.filter(p =>
        p.name.toLowerCase().includes(lowerQuery) ||
        p.brand?.toLowerCase().includes(lowerQuery)
      )
    } catch (error: any) {
      if (error.response?.status === 401) {
        await this.authenticate()
        return this.searchProducts(query)
      }
      throw error
    }
  }

  getImageUrl(imageId: string): string {
    // Image URLs don't require authentication
    return `${API_URL}/files/${imageId}/image`
  }

  async updateProduct(productId: string, productData: Partial<Product>): Promise<Product> {
    const response = await axios.put<Product>(
      `${API_URL}/products/${productId}`,
      productData,
      { headers: this.getHeaders() }
    )
    return response.data
  }

  async deleteProduct(productId: string): Promise<void> {
    await axios.delete(
      `${API_URL}/products/${productId}`,
      { headers: this.getHeaders() }
    )
  }

  async uploadImage(file: File): Promise<{ id: string }> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await axios.post<{ id: string, _id?: string }>(
      `${API_URL}/files`,
      formData,
      {
        headers: {
          ...this.getHeaders(),
          'Content-Type': 'multipart/form-data'
        }
      }
    )

    // Handle both 'id' and '_id' response formats
    return { id: response.data.id || response.data._id || '' }
  }

  async addImageByUrl(imageUrl: string, productId: string): Promise<string> {
    // Download image from URL and upload it
    const response = await axios.get(imageUrl, { responseType: 'blob' })
    const filename = imageUrl.split('/').pop() || 'image.jpg'
    const file = new File([response.data], filename, { type: response.data.type })
    const uploaded = await this.uploadImage(file)
    return uploaded.id
  }

  isAuthenticated(): boolean {
    return !!this.token
  }

  async login(username: string, password: string): Promise<void> {
    await this.authenticate(username, password)
  }

  logout(): void {
    this.token = null
  }
}

export const api = new ApiService()

// Don't auto-authenticate on load
// UPC lookup and images work without authentication
// Admin users must log in manually at /admin
