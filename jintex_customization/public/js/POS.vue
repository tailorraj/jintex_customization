<template>
  <div class="jintex-pos">
    <div class="pos-topbar">
      <div class="topbar-left">
        <h1 class="pos-brand">Jintex POS</h1>
      </div>
      
      <div class="topbar-center">
        <div class="search-container">
          <svg class="search-icon" width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M9 17A8 8 0 1 0 9 1a8 8 0 0 0 0 16zM19 19l-4.35-4.35" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <input 
            type="text" 
            v-model="searchTerm" 
            @input="onSearch"
            placeholder="Search Part Code..."
            class="search-input"
          />
          <button v-if="searchTerm" @click="clearSearch" class="clear-btn">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        
        <div class="topbar-filters">
          <select v-model="selectedItemGroup" @change="loadItems" class="topbar-select">
            <option value="">Group</option>
            <option v-for="group in itemGroups" :key="group.name" :value="group.name">
              {{ group.item_group_name }}
            </option>
          </select>
          
          <select v-model="selectedCategory" @change="loadItems" class="topbar-select">
            <option value="">Category</option>
            <option v-for="cat in categories" :key="cat.name" :value="cat.name">
              {{ cat.category_name }}
            </option>
          </select>
          
          <div class="grid-toggle">
            <button 
              @click="gridColumns = 3" 
              :class="['grid-toggle-btn', { active: gridColumns === 3 }]"
              title="3 columns"
            >
              3
            </button>
            <button 
              @click="gridColumns = 4" 
              :class="['grid-toggle-btn', { active: gridColumns === 4 }]"
              title="4 columns"
            >
              4
            </button>
          </div>
        </div>
      </div>
      
      <div class="topbar-right">
        <button class="view-orders-btn">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
            <polyline points="10 9 9 9 8 9"/>
          </svg>
          Sales Order List
        </button>
      </div>
    </div>

    <div class="pos-content">
      <div class="items-section">
        <div class="items-grid-container">
          <div class="items-grid" :class="'grid-cols-' + gridColumns">
            <div 
              v-for="item in items" 
              :key="item.name" 
              class="item-card"
            >
              <div class="item-image-section">
                <img 
                  v-if="item.image" 
                  :src="item.image" 
                  :alt="item.item_name"
                  @error="handleImageError"
                />
                <div v-else class="no-image">
                  <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                    <circle cx="8.5" cy="8.5" r="1.5"/>
                    <polyline points="21 15 16 10 5 21"/>
                  </svg>
                </div>
              </div>

              <div class="item-details">
                <div class="item-code">{{ item.jintex_item_codes || item.name }}</div>
                <h3 class="item-title">{{ item.item_name }}</h3>
                
                <div v-if="item.aliases !== '-'" class="item-aliases">
                  Aliases : {{ item.aliases }}
                </div>
                
                <div class="item-meta">
                  <span>Item Group : {{ item.item_group }}</span>
                </div>
                
                <div class="item-meta-bold">
                  <span>Category : <strong>{{ item.category }}</strong></span>
                </div>

                <div class="stock-row">
                  <div class="stock-card blr-card" :class="{'low-stock-card': item.banglore <= item.blr_reorder}">
                    <div class="stock-header">{{ item.bangalore_bin || '?' }}</div>
                    <div class="stock-quantity">Stock: {{ formatStock(item.banglore) }} Pcs</div>
                  </div>
                  <div class="stock-card amd-card" :class="{'low-stock-card': item.ahmedabad <= item.amd_reorder}">
                    <div class="stock-header">{{ item.ahmedabad_bin || '?' }}</div>
                    <div class="stock-quantity">Stock: {{ formatStock(item.ahmedabad) }} Pcs</div>
                  </div>
                </div>

                <div v-if="item.po_qty > 0" class="transit-info">
                  <span>Transit Quantity : {{ formatStock(item.po_qty) }} Pcs</span>
                  <span class="transit-date">{{ formatDate(item.po_name) }}</span>
                </div>

                <div class="prices-grid">
                  <div class="price-item">
                    <div class="price-label">Purchase</div>
                    <div class="price-value-container">
                        <span class="price-value">{{ formatAmount(item.purchase || 9) }}</span>
                    </div>
                  </div>
                  <div class="price-item">
                    <div class="price-label">Dealer</div>
                    <div class="price-value-container hover-reveal">
                      <span class="price-mask">*****</span>
                      <span class="price-value">{{ formatAmount(item.dealer) }}</span>
                      <button @click="copyPrice(item, item.dealer)" class="copy-btn" title="Copy">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                        </svg>
                      </button>
                    </div>
                  </div>
                  <div class="price-item">
                    <div class="price-label">Prime</div>
                    <div class="price-value-container hover-reveal">
                      <span class="price-mask">*****</span>
                      <span class="price-value">{{ formatAmount(item.retail) }}</span>
                      <button @click="copyPrice(item, item.retail)" class="copy-btn" title="Copy">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                        </svg>
                      </button>
                    </div>
                  </div>
                  <div class="price-item">
                    <div class="price-label">Inclusive</div>
                    <div class="price-value-container hover-reveal">
                      <span class="price-mask">*****</span>
                      <span class="price-value">{{ formatAmount(item.price3 || item.retail) }}</span>
                      <button @click="copyPrice(item, item.price3 || item.retail)" class="copy-btn" title="Copy">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>

                <div class="item-actions">
                  <button @click="addToCart(item)" class="cart-btn">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <circle cx="9" cy="21" r="1"/>
                      <circle cx="20" cy="21" r="1"/>
                      <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
                    </svg>
                  </button>
                  <button @click="onMrqClick(item)" class="mrq-btn">MRQ</button>
                </div>
              </div>
            </div>
          </div>

          <div v-if="loading" class="loading-overlay">
            <div class="spinner"></div>
          </div>

          <div v-if="!loading && hasMore" class="load-more-container">
            <button @click="loadMore" class="load-more-btn">Load More Items</button>
          </div>
        </div>
      </div>

      <div class="cart-section">
        <div class="customer-search">
          <svg class="search-icon" width="18" height="18" viewBox="0 0 20 20" fill="none">
            <path d="M9 17A8 8 0 1 0 9 1a8 8 0 0 0 0 16zM19 19l-4.35-4.35" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <input 
            type="text" 
            v-model="customerSearch"
            @input="searchCustomers"
            @focus="searchCustomers"
            placeholder="Select / Add Customer..."
            class="customer-input"
          />
          <button v-if="selectedCustomer" @click="clearCustomer" class="clear-customer-btn">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
          
          <div v-if="showCustomerDropdown && customerResults.length > 0" class="customer-dropdown">
            <div 
              v-for="customer in customerResults" 
              :key="customer.name"
              @click="selectCustomer(customer)"
              class="customer-option"
            >
              <div class="customer-name">{{ customer.customer_name }}</div>
              <div class="customer-code">{{ customer.name }}</div>
            </div>
          </div>
        </div>

        <div v-if="selectedCustomer" class="selected-customer">
          <div class="customer-badge">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
            <span>{{ selectedCustomer.customer_name }}</span>
          </div>
        </div>

        <div class="cart-items-container">
          <div v-if="cartItems.length === 0" class="empty-cart">
            <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
              <circle cx="9" cy="21" r="1"/>
              <circle cx="20" cy="21" r="1"/>
              <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
            </svg>
            <p>Cart is empty</p>
          </div>

          <div v-else class="cart-items">
            <div v-for="(item, index) in cartItems" :key="index" class="cart-item">
              <div class="cart-item-image">
                <img 
                  v-if="item.image" 
                  :src="item.image" 
                  :alt="item.item_name"
                />
                <div v-else class="no-image-small">
                  <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <rect x="3" y="3" width="18" height="18" rx="2"/>
                  </svg>
                </div>
              </div>
              
              <div class="cart-item-info">
                <div class="cart-item-header">
                  <div>
                    <div class="cart-item-name">{{ item.item_name }}</div>
                    <div class="cart-item-code">{{ item.item_code }}</div>
                  </div>
                  <button @click="removeFromCart(index)" class="remove-btn">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <polyline points="3 6 5 6 21 6"/>
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                    </svg>
                  </button>
                </div>
                
                <div v-if="item.remarks" class="cart-item-remarks">
                  Remarks : {{ item.remarks }}
                </div>
                
                <div class="cart-item-footer">
                  <div class="quantity-selector">
                    <button @click="decrementQuantity(index)" class="qty-btn">-</button>
                    <input 
                      type="number" 
                      v-model.number="item.qty"
                      @change="updateItemTotal(index)"
                      class="qty-input"
                      min="1"
                    />
                    <button @click="incrementQuantity(index)" class="qty-btn">+</button>
                  </div>
                  
                  <div class="cart-item-price">
                    <span class="price-label">{{ item.qty }} Pcs</span>
                    <span class="price-amount">₹ {{ formatAmount(item.rate) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="remarks-section">
          <label class="remarks-label">Remarks</label>
          <textarea 
            v-model="orderRemarks"
            class="remarks-textarea"
            rows="2"
            placeholder="Add order remarks..."
          ></textarea>
        </div>

        <div class="cart-summary">
          <div class="summary-row">
            <span class="summary-label">Total Quantity :</span>
            <span class="summary-value">{{ totalQuantity }} Pcs</span>
          </div>
          <div class="summary-row total-row">
            <span class="summary-label">Total Amount :</span>
            <span class="summary-value">Rs {{ formatAmount(cartTotal) }}</span>
          </div>
          
          <button 
            @click="submitOrder" 
            :disabled="cartItems.length === 0 || !selectedCustomer"
            class="submit-btn"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
            Submit & Print
          </button>
        </div>
      </div>
    </div>

    <div v-if="showItemModal" class="modal-overlay" @click="closeItemModal">
      <div class="compact-modal" @click.stop>
        <div class="modal-header">
          <h3>Add to Cart</h3>
          <button @click="closeItemModal" class="modal-close">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        
        <div class="modal-body-compact">
          <div class="modal-item-row">
            <div class="modal-item-img">
              <img 
                v-if="currentItem.image" 
                :src="currentItem.image" 
                :alt="currentItem.item_name"
              />
              <div v-else class="no-image-sm">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <rect x="3" y="3" width="18" height="18" rx="2"/>
                </svg>
              </div>
            </div>
            
            <div class="modal-item-details">
              <div class="modal-item-code">{{ currentItem.jintex_item_codes || currentItem.name }}</div>
              <div class="modal-item-name">{{ currentItem.item_name }}</div>
              <div class="modal-stock-row">
                <span class="stock-chip">BLR: {{ formatStock(currentItem.banglore) }}</span>
                <span class="stock-chip">AMD: {{ formatStock(currentItem.ahmedabad) }}</span>
              </div>
            </div>
          </div>

          <div class="modal-form-compact">
            <div class="form-row">
              <label>Price Type</label>
              <div class="price-radios-compact">
                <label class="radio-compact">
                  <input type="radio" v-model="modalPriceType" value="dealer" />
                  <span>Dealer</span>
                  <span class="radio-price">₹{{ formatAmount(currentItem.dealer) }}</span>
                </label>
                <label class="radio-compact">
                  <input type="radio" v-model="modalPriceType" value="retail" />
                  <span>Prime</span>
                  <span class="radio-price">₹{{ formatAmount(currentItem.retail) }}</span>
                </label>
                <label class="radio-compact">
                  <input type="radio" v-model="modalPriceType" value="price3" />
                  <span>Inclusive</span>
                  <span class="radio-price">₹{{ formatAmount(currentItem.price3 || currentItem.retail) }}</span>
                </label>
              </div>
            </div>

            <div class="form-row">
              <label>Price</label>
              <input 
                type="number" 
                v-model.number="modalPrice"
                class="input-compact"
                step="0.01"
                min="0"
              />
            </div>

            <div class="form-row">
              <label>Quantity</label>
              <div class="qty-control-compact wide-qty">
                <button @click="modalQuantity = Math.max(1, modalQuantity - 1)" class="qty-btn-sm">-</button>
                <input type="number" v-model.number="modalQuantity" class="qty-input-sm" min="1" />
                <button @click="modalQuantity++" class="qty-btn-sm">+</button>
              </div>
            </div>

            <div class="form-row">
              <label>Remarks</label>
              <textarea 
                v-model="modalRemarks"
                class="textarea-compact"
                rows="2"
                placeholder="Optional remarks..."
              ></textarea>
            </div>

            <div class="modal-total-compact">
              <span>Total:</span>
              <span class="total-value">₹ {{ (modalQuantity * modalPrice).toFixed(2) }}</span>
            </div>
          </div>
        </div>
        
        <div class="modal-footer-compact">
          <button @click="closeItemModal" class="btn-secondary-sm">Cancel</button>
          <button @click="addToCartFromModal" class="btn-primary-sm">Add to Cart</button>
        </div>
      </div>
    </div>

    <div v-if="showMrqModal" class="modal-overlay" @click="closeMrqModal">
      <div class="compact-modal" @click.stop>
        <div class="modal-header">
          <h3>Create Material Request</h3>
          <button @click="closeMrqModal" class="modal-close">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div class="modal-body-compact">
          <div class="warning-box">
             <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
               <circle cx="12" cy="12" r="10"></circle>
               <line x1="12" y1="8" x2="12" y2="12"></line>
               <line x1="12" y1="16" x2="12.01" y2="16"></line>
             </svg>
             <span>{{ mrqMessage }}</span>
          </div>
          
          <div class="modal-form-compact">
            <div class="form-row">
              <label>Item</label>
              <div class="static-value">{{ mrqItem ? mrqItem.item_name : '' }}</div>
            </div>

            <div class="form-row">
              <label>Quantity to Request</label>
              <input 
                type="number" 
                v-model.number="mrqQty"
                class="input-compact"
                min="1"
              />
            </div>

            <div class="form-row">
              <label>Warehouse</label>
              <select v-model="mrqWarehouse" class="input-compact">
                <option value="" disabled>Select Warehouse</option>
                <option v-for="wh in warehouses" :key="wh" :value="wh">{{ wh }}</option>
              </select>
            </div>
          </div>
        </div>

        <div class="modal-footer-compact">
          <button @click="closeMrqModal" class="btn-secondary-sm">Cancel</button>
          <button @click="submitMrq" class="btn-primary-sm">Create MR</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
export default {
  name: 'JintexPOS',
  data() {
    return {
      items: [],
      itemGroups: [],
      categories: [],
      cartItems: [],
      customerResults: [],
      
      searchTerm: '',
      selectedItemGroup: '',
      selectedCategory: '',
      customerSearch: '',
      selectedCustomer: null,
      orderRemarks: '',
      
      loading: false,
      showItemModal: false,
      showCustomerDropdown: false,
      currentItem: null,
      modalQuantity: 1,
      modalPriceType: 'dealer',
      modalPrice: 0,
      modalRemarks: '',
      
      searchTimeout: null,
      customerSearchTimeout: null,
      
      gridColumns: 3,
      offset: 0,
      limit: 15,
      hasMore: true,

      // MRQ Logic
      showMrqModal: false,
      mrqItem: null,
      mrqMessage: '',
      mrqQty: 1,
      mrqWarehouse: '',
      warehouses: [] // Fetched dynamically
    };
  },
  
  computed: {
    cartTotal() {
      return this.cartItems.reduce((sum, item) => sum + item.amount, 0);
    },
    totalQuantity() {
      return this.cartItems.reduce((sum, item) => sum + item.qty, 0);
    }
  },
  
  mounted() {
    this.init();
    document.addEventListener('click', this.handleClickOutside);
    // Hide Frappe's default page header/breadcrumbs
    const pageHead = document.querySelector('.page-head');
    if (pageHead) pageHead.style.display = 'none';
  },
  
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside);
    // Restore Frappe's default page header
    const pageHead = document.querySelector('.page-head');
    if (pageHead) pageHead.style.display = '';
  },
  
  methods: {
    async init() {
      await this.loadItemGroups();
      await this.loadCategories();
      await this.fetchWarehouses();
      await this.loadItems();
    },

    async fetchWarehouses() {
      try {
        const response = await frappe.call({
          method: 'frappe.client.get_list',
          args: {
            doctype: 'Warehouse',
            // filters: {
            //   status: 'Enabled'
            // },
            fields: ['name'],
            limit_page_length: 0
          }
        });
        
        if (response.message) {
          this.warehouses = response.message.map(w => w.name);
        }
      } catch (error) {
        console.error('Failed to load warehouses:', error);
        frappe.msgprint('Could not fetch active warehouses');
      }
    },
    
    async loadItemGroups() {
      try {
        const response = await frappe.call({
          method: 'jintex_customization.jintex_management.page.pos.pos.get_item_groups',
        });
        this.itemGroups = response.message || [];
      } catch (error) {
        console.error('Failed to load item groups:', error);
      }
    },
    
    async loadCategories() {
      try {
        const response = await frappe.call({
          method: 'jintex_customization.jintex_management.page.pos.pos.get_categories',
        });
        this.categories = response.message || [];
      } catch (error) {
        console.error('Failed to load categories:', error);
      }
    },
    
    async loadItems(reset = true) {
      if (reset) {
        this.offset = 0;
        this.items = [];
      }
      
      this.loading = true;
      try {
        const response = await frappe.call({
          method: 'jintex_customization.jintex_management.page.pos.pos.get_items',
          args: {
            product_id: this.searchTerm,
            item_group: this.selectedItemGroup,
            category: this.selectedCategory,
            offset: this.offset,
            limit: this.limit
          }
        });
        
        const newItems = response.message || [];
        
        if (reset) {
          this.items = newItems;
        } else {
          this.items = [...this.items, ...newItems];
        }
        
        this.hasMore = newItems.length === this.limit;
        
      } catch (error) {
        frappe.msgprint({
          title: 'Error',
          message: 'Failed to load items',
          indicator: 'red'
        });
      } finally {
        this.loading = false;
      }
    },
    
    loadMore() {
      this.offset += this.limit;
      this.loadItems(false);
    },
    
    onSearch() {
      clearTimeout(this.searchTimeout);
      this.searchTimeout = setTimeout(() => {
        this.loadItems();
      }, 300);
    },
    
    clearSearch() {
      this.searchTerm = '';
      this.loadItems();
    },
    
    async searchCustomers() {
      clearTimeout(this.customerSearchTimeout);
      this.customerSearchTimeout = setTimeout(async () => {
        try {
          const response = await frappe.call({
            method: 'jintex_customization.jintex_management.page.pos.pos.get_customers',
            args: {
              search_term: this.customerSearch || ''
            }
          });
          this.customerResults = response.message || [];
          this.showCustomerDropdown = true;
        } catch (error) {
          console.error('Failed to search customers:', error);
        }
      }, 300);
    },
    
    selectCustomer(customer) {
      this.selectedCustomer = customer;
      this.customerSearch = customer.customer_name;
      this.showCustomerDropdown = false;
      this.customerResults = [];
    },
    
    clearCustomer() {
      this.selectedCustomer = null;
      this.customerSearch = '';
    },
    
    handleClickOutside(event) {
      if (!event.target.closest('.customer-search')) {
        this.showCustomerDropdown = false;
      }
    },
    
    addToCart(item) {
      this.currentItem = { ...item };
      this.modalQuantity = 1;
      this.modalPriceType = 'dealer';
      this.modalPrice = parseFloat(item.dealer) || 0;
      this.modalRemarks = '';
      this.showItemModal = true;
    },
    
    async copyPrice(item, price) {
       const code = item.jintex_item_codes || item.name;
        const textToCopy = `${code} ${item.item_name} @ ${this.formatAmount(price)}`;

        // 2. Try Modern API (HTTPS)
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(textToCopy).then(() => {
            frappe.show_alert({ message: 'Copied!', indicator: 'green' });
            }).catch((err) => {
            console.error('Async: Could not copy text: ', err);
            });
        } 
        // 3. Fallback for HTTP / Older Browsers
        else {
            const textArea = document.createElement("textarea");
            textArea.value = textToCopy;
            
            // Ensure it's not visible but part of the DOM
            textArea.style.position = "fixed";
            textArea.style.left = "-9999px";
            textArea.style.top = "0";
            document.body.appendChild(textArea);
            
            textArea.focus();
            textArea.select();
            
            try {
            const successful = document.execCommand('copy');
            if (successful) {
                frappe.show_alert({ message: 'Copied!', indicator: 'green' });
            } else {
                frappe.msgprint('Unable to copy');
            }
            } catch (err) {
            console.error('Fallback: Oops, unable to copy', err);
            }
            
            document.body.removeChild(textArea);
        }
    },
    
    addToCartFromModal() {
      if (this.modalQuantity <= 0) {
        frappe.msgprint('Quantity must be greater than 0');
        return;
      }
      
      if (!this.modalPrice || this.modalPrice <= 0) {
        frappe.msgprint('Price must be greater than 0');
        return;
      }
      
      const cartItem = {
        item_code: this.currentItem.name,
        item_name: this.currentItem.item_name,
        qty: this.modalQuantity,
        rate: this.modalPrice,
        amount: this.modalQuantity * this.modalPrice,
        uom: 'Nos',
        remarks: this.modalRemarks,
        image: this.currentItem.image
      };
      
      this.cartItems.push(cartItem);
      this.closeItemModal();
      frappe.show_alert({
        message: `${this.currentItem.item_name} added to cart`,
        indicator: 'green'
      });
    },
    
    closeItemModal() {
      this.showItemModal = false;
      this.currentItem = null;
    },
    
    incrementQuantity(index) {
      this.cartItems[index].qty++;
      this.updateItemTotal(index);
    },
    
    decrementQuantity(index) {
      if (this.cartItems[index].qty > 1) {
        this.cartItems[index].qty--;
        this.updateItemTotal(index);
      }
    },
    
    updateItemTotal(index) {
      const item = this.cartItems[index];
      item.amount = item.qty * item.rate;
    },
    
    removeFromCart(index) {
      frappe.confirm(
        `Remove ${this.cartItems[index].item_name} from cart?`,
        () => {
          this.cartItems.splice(index, 1);
        }
      );
    },
    
    async submitOrder() {
      if (!this.selectedCustomer) {
        frappe.msgprint('Please select a customer');
        return;
      }
      
      if (this.cartItems.length === 0) {
        frappe.msgprint('Cart is empty');
        return;
      }
      
      try {
        const response = await frappe.call({
          method: 'jintex_customization.jintex_management.page.pos.pos.create_sales_order',
          args: {
            customer: this.selectedCustomer.name,
            items: this.cartItems,
            remarks: this.orderRemarks
          }
        });
        
        frappe.show_alert({
          message: `Sales Order ${response.message.name} created successfully`,
          indicator: 'green'
        });
        
        // Clear cart
        this.cartItems = [];
        this.orderRemarks = '';
        this.selectCustomer = null;

        const url = `/desk/print/Sales Order/${response.message.name}`;
        
        // 3. Open in a new tab
        window.open(url, '_blank');

        
      } catch (error) {
        frappe.msgprint({
          title: 'Error',
          message: error.message || 'Failed to create sales order',
          indicator: 'red'
        });
      }
    },

    // --- MRQ Logic ---
    async onMrqClick(item) {
      this.mrqItem = item;
      this.mrqQty = 1;
      this.mrqWarehouse = '';
      this.mrqMessage = 'Checking...';
      
      try {
        const response = await frappe.call({
          method: 'jintex_customization.jintex_management.page.material_request_pag.material_request_pag.check_purchase_material',
          args: {
            product_id: item.name
          }
        });
        
        this.mrqMessage = "Quantity to be Received: " + (response.message || '0');
        this.showMrqModal = true;
        
      } catch (error) {
        frappe.msgprint('Failed to check purchase material');
        console.error(error);
      }
    },

    closeMrqModal() {
      this.showMrqModal = false;
      this.mrqItem = null;
    },

    async submitMrq() {
      if (!this.mrqQty || this.mrqQty <= 0) {
        frappe.msgprint("Please enter a valid quantity");
        return;
      }
      if (!this.mrqWarehouse) {
        frappe.msgprint("Please select a warehouse");
        return;
      }

      try {
        const response = await frappe.call({
          method: 'jintex_customization.jintex_management.page.show_items.show_items.send_material_request',
          args: {
            product_id: this.mrqItem.name,
            qty: this.mrqQty,
            warehouse: this.mrqWarehouse
          }
        });

        if (response.message === "Success") {
          frappe.msgprint({
             title: 'Success',
             message: "Material Request Created Successfully!",
             indicator: 'green'
          });
          this.closeMrqModal();
        } else {
             frappe.msgprint(response.message || "Request processed");
             this.closeMrqModal();
        }
      } catch (error) {
        frappe.msgprint("Failed to create Material Request");
        console.error(error);
      }
    },
    
    formatStock(value) {
      if (!value || value === '0' || value === '-') return '0';
      return parseFloat(value).toString();
    },
    
    // Updated to always show 2 decimal places
    formatAmount(amount) {
      const val = parseFloat(amount || 0);
      return val.toFixed(2);
    },
    
    formatDate(date) {
      if (!date || date === '-') return '-';
      return frappe.datetime.str_to_user(date);
    },
    
    handleImageError(e) {
      e.target.style.display = 'none';
    }
  },
  
  watch: {
    modalPriceType(newType) {
      if (this.currentItem) {
        this.modalPrice = parseFloat(this.currentItem[newType]) || 0;
      }
    }
  }
};
</script>

<style scoped>
/* Same base styles */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.jintex-pos {
  height: calc(100vh);
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* ... Topbar styles ... */
.pos-topbar {
  background: white;
  padding: 0.75rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  z-index: 100;
}
.topbar-left { flex-shrink: 0; }
.pos-brand { font-size: 1.35rem; font-weight: 700; color: #2563eb; margin: 0; }
.topbar-center { flex: 1; display: flex; gap: 1rem; align-items: center; }
.search-container { position: relative; flex: 1; max-width: 400px; }
.search-icon { position: absolute; left: 1rem; top: 50%; transform: translateY(-50%); color: #94a3b8; pointer-events: none; }
.search-input { width: 100%; padding: 0 3rem; height: 46px; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 0.95rem; display: flex; align-items: center; }
.search-input:focus { outline: none; border-color: #3b82f6; }
.clear-btn { position: absolute; right: 0.75rem; top: 50%; transform: translateY(-50%); width: 28px; height: 28px; border: none; background: #f1f5f9; border-radius: 6px; cursor: pointer; color: #64748b; display: flex; align-items: center; justify-content: center; }
.topbar-filters { display: flex; gap: 0.75rem; align-items: center; }
.topbar-select { padding: 0 2rem 0 1rem; height: 46px; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 0.95rem; color: #64748b; background: white; cursor: pointer; min-width: 140px; line-height: 44px; }
.grid-toggle { display: flex; gap: 0.25rem; background: #f1f5f9; padding: 4px; border-radius: 8px; height: 46px; align-items: center; }
.grid-toggle-btn { padding: 0 0.75rem; height: 100%; border: none; background: transparent; border-radius: 6px; cursor: pointer; font-size: 0.85rem; font-weight: 600; color: #64748b; }
.grid-toggle-btn.active { background: white; color: #3b82f6; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.view-orders-btn { display: flex; align-items: center; gap: 0.5rem; padding: 0 1.25rem; height: 46px; background: #dbeafe; color: #1e40af; border: none; border-radius: 8px; font-size: 0.9rem; font-weight: 600; cursor: pointer; }

/* Content Grid */
.pos-content {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 420px;
  gap: 0;
  overflow: hidden;
}
.items-section { background: white; display: flex; flex-direction: column; overflow: hidden; }
.items-grid-container { flex: 1; overflow-y: auto; overflow-x: hidden; position: relative; }
.items-grid { display: grid; gap: 1.25rem; padding: 1.5rem; }
.items-grid.grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
.items-grid.grid-cols-4 { grid-template-columns: repeat(4, 1fr); }

/* Item Card Typography Updated */
.item-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  overflow: hidden;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
}
.item-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-color: #3b82f6; transform: translateY(-2px); }

.item-image-section {
  width: 100%;
  height: 200px; /* 1. Enforce fixed height to align grid */
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border-bottom: 1px solid #e5e7eb;
}

.item-image-section img { 
  width: 100%; 
  height: 100%; 
  object-fit: contain; /* 2. Ensures image is fully visible & centered */
}
.no-image { color: #cbd5e1; }

.item-details { padding: 1rem; display: flex; flex-direction: column; gap: 0.5rem; }

/* Item Code: Large, Bold, Purple/Blue */
.item-code {
  font-size: 1.1rem;
  font-weight: 800;
  color: #4f46e5; /* Indigo-600 */
  margin-bottom: 0.25rem;
}

/* Item Name: Black, Bold */
.item-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #0f172a; /* Slate-900 */
  margin: 0;
  line-height: 1.3;
}

.item-aliases { font-size: 0.8rem; color: #64748b; line-height: 1.4; }
.item-meta { font-size: 0.8rem; color: #475569; }
.item-meta-bold { font-size: 0.8rem; color: #0f172a; font-weight: 700;}

/* Stock Cards - Specific Colors */
.stock-row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin: 0.5rem 0; }

.stock-card {
  border-radius: 4px;
  padding: 0.5rem;
  text-align: center;
  border: 1px solid transparent;
}

/* Bangalore: Pink/Red Theme */
.blr-card {
  background-color: #fce7f3; /* Pink-100 */
  color: #9d174d; /* Pink-800 */
  border-color: #fbcfe8;
}

/* Ahmedabad: Green Theme */
.amd-card {
  background-color: #dcfce7; /* Green-100 */
  color: #166534; /* Green-800 */
  border-color: #bbf7d0;
}

.stock-header {
  font-size: 0.9rem; /* Increased size */
  font-weight: 800;
  margin-bottom: 0.15rem;
}

.stock-quantity {
  font-size: 0.85rem;
  font-weight: 600;
}

/* Prices Grid */
.prices-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.5rem;
  margin: 0.5rem 0;
  padding-top: 0.5rem;
  border-top: 1px dashed #e5e7eb;
}

.price-item { text-align: center; }
.price-label { font-size: 0.7rem; color: #64748b; font-weight: 500; display: block; margin-bottom: 0.25rem; }

/* Masking Logic */
.price-value-container {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 20px;
}

.price-mask {
  display: block;
  font-weight: 700;
  color: #94a3b8;
  letter-spacing: 2px;
}

.price-value {
  display: none; /* Hidden by default */
  font-size: 0.95rem;
  font-weight: 700;
  color: #1e293b;
}

/* Reveal on Hover */
.hover-reveal:hover .price-mask { display: none; }
.hover-reveal:hover .price-value { display: block; }
.hover-reveal:hover .copy-btn { opacity: 1; }

.copy-btn {
  position: absolute;
  top: -8px;
  right: -12px;
  width: 18px;
  height: 18px;
  padding: 0;
  border: none;
  background: #3b82f6;
  color: white;
  border-radius: 3px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.2s;
  z-index: 10;
}

/* Actions Grid (80/20) */
.item-actions {
  display: grid;
  grid-template-columns: 3fr 2fr;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.cart-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  width: 100%;
}
.cart-btn:hover { background-color: #2563eb; }

.mrq-btn {
  padding: 0.5rem;
  background: #fecaca;
  color: #991b1b;
  border: 1px solid #f87171;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.mrq-btn:hover { background: #ef4444; color: white; }


/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 2rem;
}

.compact-modal {
  background: white;
  border-radius: 12px;
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 50px rgba(0,0,0,0.3);
}

.modal-header { padding: 1rem 1.25rem; border-bottom: 1px solid #e5e7eb; display: flex; justify-content: space-between; align-items: center; }
.modal-header h3 { font-size: 1.1rem; font-weight: 700; color: #1e293b; margin: 0; }
.modal-close { width: 32px; height: 32px; border: none; background: #f1f5f9; border-radius: 6px; cursor: pointer; color: #64748b; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.modal-close:hover { background: #e2e8f0; }

.modal-body-compact { padding: 1.25rem; overflow-y: auto; max-height: calc(90vh - 140px); }

.modal-item-row { display: flex; gap: 1rem; margin-bottom: 1.25rem; padding-bottom: 1.25rem; border-bottom: 1px solid #e5e7eb; }
.modal-item-img { width: 80px; height: 80px; flex-shrink: 0; border-radius: 8px; overflow: hidden; background: #f8fafc; display: flex; align-items: center; justify-content: center; }
.modal-item-img img { width: 100%; height: 100%; object-fit: cover; }
.no-image-sm { color: #cbd5e1; }

.modal-item-details { flex: 1; }
.modal-item-code { font-size: 0.85rem; font-weight: 700; color: #5b21b6; margin-bottom: 0.25rem; }
.modal-item-name { font-size: 1rem; font-weight: 600; color: #1e293b; margin-bottom: 0.5rem; line-height: 1.3; }
.modal-stock-row { display: flex; gap: 0.5rem; }
.stock-chip { padding: 0.25rem 0.5rem; background: #dbeafe; color: #1e40af; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }

.modal-form-compact { display: flex; flex-direction: column; gap: 1rem; }
.form-row { display: flex; flex-direction: column; gap: 0.5rem; }
.form-row label { font-weight: 600; color: #475569; font-size: 0.85rem; }

.price-radios-compact { display: flex; flex-direction: column; gap: 0.5rem; }
.radio-compact { display: flex; align-items: center; gap: 0.5rem; padding: 0.625rem 0.75rem; border: 2px solid #e2e8f0; border-radius: 6px; cursor: pointer; transition: all 0.2s; }
.radio-compact:hover { border-color: #3b82f6; background: #f8fafc; }
.radio-compact input[type="radio"] { cursor: pointer; }
.radio-compact span:nth-child(2) { flex: 1; font-weight: 500; color: #1e293b; font-size: 0.9rem; }
.radio-price { font-weight: 700; color: #3b82f6; font-size: 0.9rem; }

.input-compact {
    padding: 0 2rem 0 1rem; height: 46px; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 0.95rem; font-weight: 600; background: white; cursor: pointer; min-width: 140px; line-height: 44px;
}
.input-compact:focus { outline: none; border-color: #3b82f6; }

.textarea-compact { padding: 0.625rem 0.75rem; border: 2px solid #e2e8f0; border-radius: 6px; font-size: 0.9rem; resize: vertical; font-family: inherit; }
.textarea-compact:focus { outline: none; border-color: #3b82f6; }

.modal-total-compact { display: flex; justify-content: space-between; align-items: center; padding: 1rem; background: #f8fafc; border-radius: 6px; margin-top: 0.5rem; }
.modal-total-compact span:first-child { font-weight: 600; color: #475569; }
.total-value { font-size: 1.5rem; font-weight: 700; color: #2563eb; }

.modal-footer-compact { padding: 1rem 1.25rem; border-top: 1px solid #e5e7eb; display: flex; gap: 0.75rem; justify-content: flex-end; }

/* Wide Qty Component */
.qty-control-compact { display: flex; align-items: center; gap: 0.75rem; }
.wide-qty .qty-input-sm { width: 120px; } /* Wider input */

/* Buttons & Inputs */
.qty-btn-sm { width: 36px; height: 36px; border: 2px solid #e2e8f0; background: white; border-radius: 6px; font-weight: 600; cursor: pointer; }
.qty-input-sm { height: 36px; text-align: center; border: 2px solid #e2e8f0; border-radius: 6px; font-weight: 600; font-size: 1rem; }
.btn-primary-sm { padding: 0.625rem 1.25rem; background: #3b82f6; color: white; border-radius: 6px; border: none; font-weight: 600; cursor: pointer; }
.btn-secondary-sm { padding: 0.625rem 1.25rem; background: #f1f5f9; color: #64748b; border-radius: 6px; border: none; font-weight: 600; cursor: pointer; }

/* Warning Box */
.warning-box { background: #fff7ed; border: 1px solid #fed7aa; color: #c2410c; padding: 0.75rem; border-radius: 6px; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.75rem; font-weight: 600; }
.static-value { padding: 0.625rem 0.75rem; background: #f1f5f9; border-radius: 6px; color: #475569; font-weight: 600; }

/* Cart Section */
.cart-section { background: #f8fafc; border-left: 1px solid #e5e7eb; display: flex; flex-direction: column; overflow: hidden; }
.customer-search { position: relative; margin: 1rem; }
.customer-input { width: 100%; padding: 0.875rem 3rem 0.875rem 3rem; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 0.95rem; transition: all 0.2s; }
.customer-input:focus { outline: none; border-color: #3b82f6; }
.clear-customer-btn { position: absolute; right: 0.75rem; top: 50%; transform: translateY(-50%); width: 28px; height: 28px; border: none; background: #f1f5f9; border-radius: 6px; cursor: pointer; color: #64748b; display: flex; align-items: center; justify-content: center; }
.customer-dropdown { position: absolute; top: 100%; left: 0; right: 0; background: white; border: 2px solid #e2e8f0; border-radius: 8px; margin-top: 0.5rem; max-height: 300px; overflow-y: auto; box-shadow: 0 10px 25px rgba(0,0,0,0.1); z-index: 100; }
.customer-option { padding: 0.875rem 1rem; cursor: pointer; transition: all 0.15s; border-bottom: 1px solid #f1f5f9; }
.customer-option:hover { background: #f8fafc; }
.customer-name { font-weight: 600; color: #1e293b; margin-bottom: 0.25rem; }
.customer-code { font-size: 0.8rem; color: #64748b; }
.selected-customer { margin: 0 1rem 1rem 1rem; }
.customer-badge { display: flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1rem; background: #dbeafe; color: #1e40af; border-radius: 8px; font-weight: 600; font-size: 0.9rem; }
.cart-items-container { flex: 1; overflow-y: auto; padding: 0 1rem; }
.empty-cart { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: #cbd5e1; }
.empty-cart p { margin-top: 1rem; color: #94a3b8; font-size: 0.95rem; }
.cart-items { display: flex; flex-direction: column; gap: 0.75rem; }
.cart-item { background: white; border-radius: 10px; padding: 1rem; display: flex; gap: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
.cart-item-image { width: 70px; height: 70px; flex-shrink: 0; border-radius: 6px; overflow: hidden; background: #f8fafc; display: flex; align-items: center; justify-content: center; }
.cart-item-image img { width: 100%; height: 100%; object-fit: cover; }
.no-image-small { color: #cbd5e1; }
.cart-item-info { flex: 1; display: flex; flex-direction: column; gap: 0.5rem; }
.cart-item-header { display: flex; justify-content: space-between; align-items: flex-start; }
.cart-item-name { font-weight: 600; color: #1e293b; font-size: 0.9rem; line-height: 1.3; }
.cart-item-code { font-size: 0.8rem; color: #64748b; margin-top: 0.125rem; }
.remove-btn { width: 28px; height: 28px; border: none; background: #fee2e2; color: #991b1b; border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; flex-shrink: 0; }
.remove-btn:hover { background: #fecaca; }
.cart-item-remarks { font-size: 0.8rem; color: #64748b; font-style: italic; background: #f8fafc; padding: 0.5rem; border-radius: 4px; }
.cart-item-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 0.25rem; }
.quantity-selector { display: flex; align-items: center; gap: 0.5rem; }
.qty-btn { width: 28px; height: 28px; border: 2px solid #e2e8f0; background: white; border-radius: 4px; cursor: pointer; font-size: 1rem; font-weight: 600; color: #64748b; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.qty-btn:hover { border-color: #3b82f6; color: #3b82f6; }
.qty-input { width: 50px; height: 28px; text-align: center; border: 2px solid #e2e8f0; border-radius: 4px; font-weight: 600; font-size: 0.9rem; }
.qty-input:focus { outline: none; border-color: #3b82f6; }
.cart-item-price { display: flex; flex-direction: column; align-items: flex-end; gap: 0.125rem; }
.price-label { font-size: 0.75rem; color: #64748b; }
.price-amount { font-size: 1rem; font-weight: 700; color: #1e293b; }
.remarks-section { margin: 1rem; }
.remarks-label { display: block; font-weight: 600; color: #475569; font-size: 0.9rem; margin-bottom: 0.5rem; }
.remarks-textarea { width: 100%; padding: 0.75rem; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 0.9rem; resize: vertical; font-family: inherit; }
.remarks-textarea:focus { outline: none; border-color: #3b82f6; }
.cart-summary { background: white; padding: 1.25rem 1rem; border-top: 1px solid #e5e7eb; }
.summary-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; font-size: 0.95rem; }
.summary-label { color: #475569; font-weight: 500; }
.summary-value { font-weight: 600; color: #1e293b; }
.total-row { font-size: 1.1rem; padding-top: 0.75rem; border-top: 2px solid #e5e7eb; margin-bottom: 1rem; }
.total-row .summary-value { font-size: 1.25rem; color: #2563eb; }
.submit-btn { width: 100%; padding: 1rem; background: #3b82f6; color: white; border: none; border-radius: 8px; font-size: 1rem; font-weight: 700; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 0.5rem; transition: all 0.2s; }
.submit-btn:hover:not(:disabled) { background: #2563eb; transform: translateY(-1px); box-shadow: 0 6px 16px rgba(37, 99, 235, 0.3); }
.submit-btn:disabled { opacity: 0.5; cursor: not-allowed; }

/* Loading */
.loading-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(255, 255, 255, 0.9); display: flex; align-items: center; justify-content: center; z-index: 10; }
.spinner { width: 48px; height: 48px; border: 4px solid #f1f5f9; border-top-color: #3b82f6; border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.load-more-container { padding: 1.5rem; text-align: center; }
.load-more-btn { padding: 0.75rem 2rem; background: #f1f5f9; color: #475569; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 0.9rem; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.load-more-btn:hover { background: white; border-color: #3b82f6; color: #3b82f6; }

/* Scrollbar */
.items-grid-container::-webkit-scrollbar, .cart-items-container::-webkit-scrollbar, .customer-dropdown::-webkit-scrollbar, .modal-body-compact::-webkit-scrollbar { width: 8px; }
.items-grid-container::-webkit-scrollbar-track, .cart-items-container::-webkit-scrollbar-track, .customer-dropdown::-webkit-scrollbar-track, .modal-body-compact::-webkit-scrollbar-track { background: #f1f5f9; }
.items-grid-container::-webkit-scrollbar-thumb, .cart-items-container::-webkit-scrollbar-thumb, .customer-dropdown::-webkit-scrollbar-thumb, .modal-body-compact::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
.items-grid-container::-webkit-scrollbar-thumb:hover, .cart-items-container::-webkit-scrollbar-thumb:hover, .customer-dropdown::-webkit-scrollbar-thumb:hover, .modal-body-compact::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

/* Responsive */
@media (max-width: 1400px) { .items-grid.grid-cols-4 { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 1200px) { .items-grid.grid-cols-3 { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 1024px) { .pos-content { grid-template-columns: 1fr; } .cart-section { display: none; } }
</style>