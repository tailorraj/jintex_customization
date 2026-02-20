<template>
  <div class="jintex-pos">
    <div class="pos-topbar">
      <div class="topbar-left">
        <h1 class="pos-brand">Jintex POS</h1>
      </div>

      <div class="topbar-center">
        <div class="search-container">
          <svg class="search-icon" width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M9 17A8 8 0 1 0 9 1a8 8 0 0 0 0 16zM19 19l-4.35-4.35" stroke="currentColor" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          <input type="text" v-model="searchTerm" @input="onSearch" placeholder="Search Part Code..."
            class="search-input" />
          <button v-if="searchTerm" @click="clearSearch" class="clear-btn">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
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
            <button @click="gridColumns = 3" :class="['grid-toggle-btn', { active: gridColumns === 3 }]"
              title="3 columns">
              3
            </button>
            <button @click="gridColumns = 4" :class="['grid-toggle-btn', { active: gridColumns === 4 }]"
              title="4 columns">
              4
            </button>
          </div>
        </div>
      </div>

      <div class="topbar-right">
        <button class="view-orders-btn" @click="showNewCustomerModal = true">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          Create New Customer
        </button>

        <button class="view-orders-btn" @click="goToSalesOrders()">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="16" y1="13" x2="8" y2="13" />
            <line x1="16" y1="17" x2="8" y2="17" />
            <polyline points="10 9 9 9 8 9" />
          </svg>
          Sales Order List
        </button>
      </div>
    </div>

    <div class="pos-content">
      <div class="items-section">
        <div class="items-grid-container">
          <div class="items-grid" :class="'grid-cols-' + gridColumns">

            <div v-for="item in items" :key="item.name" class="item-card">
              <div class="image-section">
                <img v-if="item.image" :src="item.image" :alt="item.item_name" @error="handleImageError" />
                <div v-else class="image-placeholder">
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"
                    stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                    <circle cx="8.5" cy="8.5" r="1.5"></circle>
                    <polyline points="21 15 16 10 5 21"></polyline>
                  </svg>
                </div>
              </div>

              <div class="product-info">
                <a class="product-sku" @click.stop.prevent="openProductDetail(item)">{{ item.jintex_item_codes ||
                  item.name }}</a>
                <div class="product-name" :title="item.item_name">{{ item.item_name }}</div>
              </div>

              <div class="meta-list">
                <div class="meta-row" v-if="item.aliases && item.aliases !== '-'">
                  <span class="meta-label">Aliases : </span>{{ item.aliases }}
                </div>
                <div class="meta-row">
                  <span class="meta-label">Item Group : </span>{{ item.item_group }}
                </div>
                <div class="meta-row">
                  <span class="meta-label">Category : </span><strong>{{ item.category }}</strong>
                </div>
              </div>

              <div class="stock-section">
                <div class="stock-badge"
                  :class="item.banglore <= item.blr_reorder ? 'stock-badge-red' : 'stock-badge-green'">
                  <div class="stock-location">{{ item.bangalore_bin || '?' }}</div>
                  <div class="stock-count">Stock: {{ formatStock(item.banglore) }}</div>
                </div>
                <div class="stock-badge"
                  :class="item.ahmedabad <= item.amd_reorder ? 'stock-badge-red' : 'stock-badge-green'">
                  <div class="stock-location">{{ item.ahmedabad_bin || '?' }}</div>
                  <div class="stock-count">Stock: {{ formatStock(item.ahmedabad) }}</div>
                </div>
              </div>

              <div class="transit-row">
                <span class="transit-item">Transit Quantity : <strong>{{ item.po_qty > 0 ? `${formatStock(item.po_qty)} Pcs`:
                    '-'}}</strong></span>
                <span class="transit-item"><strong>{{ item.po_qty > 0 ? formatDate(item.po_name) : '-'}}</strong></span>
              </div>

              <div class="divider spacer-top"></div>

              <div class="price-row">
                <div class="price-col">
                  <span class="price-col-label">Purchase</span>
                  <span class="price-col-value">
                    <span class="price-col-masked">*****</span>
                    <span class="price-col-actual">{{ formatAmount(item.purchase || 0) }}</span>
                    <button class="copy-btn" @click.stop="copyPrice(item, item.purchase || 0, $event)" title="Copy">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                        stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="9" y="9" width="13" height="13" rx="2" />
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                      </svg>
                    </button>
                  </span>
                </div>
                <div class="price-col">
                  <span class="price-col-label">Dealer</span>
                  <span class="price-col-value">
                    <span class="price-col-masked">*****</span>
                    <span class="price-col-actual">₹{{ formatAmount(item.dealer) }}</span>
                    <button class="copy-btn" @click.stop="copyPrice(item, item.dealer, $event)" title="Copy">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                        stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="9" y="9" width="13" height="13" rx="2" />
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                      </svg>
                    </button>
                  </span>
                </div>
                <div class="price-col">
                  <span class="price-col-label">Prime</span>
                  <span class="price-col-value">
                    <span class="price-col-masked">*****</span>
                    <span class="price-col-actual">₹{{ formatAmount(item.prime) }}</span>
                    <button class="copy-btn" @click.stop="copyPrice(item, item.prime, $event)" title="Copy">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                        stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="9" y="9" width="13" height="13" rx="2" />
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                      </svg>
                    </button>
                  </span>
                </div>
                <div class="price-col">
                  <span class="price-col-label">Inclusive</span>
                  <span class="price-col-value">
                    <span class="price-col-masked">*****</span>
                    <span class="price-col-actual">₹{{ formatAmount(item.inclusive || 0) }}</span>
                    <button class="copy-btn" @click.stop="copyPrice(item, item.inclusive || 0, $event)" title="Copy">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                        stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="9" y="9" width="13" height="13" rx="2" />
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                      </svg>
                    </button>
                  </span>
                </div>
              </div>

              <div class="divider"></div>

              <div class="actions">
                <button class="btn-cart" @click="addToCart(item)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                    stroke-linejoin="round">
                    <circle cx="9" cy="21" r="1" />
                    <circle cx="20" cy="21" r="1" />
                    <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
                  </svg>
                  Add to Cart
                </button>
                <button class="btn-mrq" @click="onMrqClick(item)">MRQ</button>
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
            <path d="M9 17A8 8 0 1 0 9 1a8 8 0 0 0 0 16zM19 19l-4.35-4.35" stroke="currentColor" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          <input type="text" v-model="customerSearch" @input="searchCustomers" @focus="searchCustomers"
            placeholder="Select / Add Customer..." class="customer-input" />
          <button v-if="selectedCustomer" @click="clearCustomer" class="clear-customer-btn">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
          
          <div v-if="showCustomerDropdown && customerResults.length > 0" class="customer-dropdown">
            <div v-for="customer in customerResults" :key="customer.name" @click="selectCustomer(customer)"
              class="customer-option">
              <div class="customer-name">{{ customer.customer_name }}</div>
              <div class="customer-code">{{ customer.mobile_no || customer.name }}</div>
            </div>
          </div>
          <div v-if="showNewCustomerModal" class="modal-overlay" @click="showNewCustomerModal = false">
            <div class="card" @click.stop style="max-width: 350px;">
              <div class="card-header">
                <h2>New Customer</h2>
              </div>
              <div class="section" style="padding-top: 10px;">
                <div class="form-row" style="margin-bottom: 15px;">
                  <label>Full Name</label>
                  <input type="text" v-model="newCustomer.name" class="price-input-field" placeholder="Enter name">
                </div>
                <div class="form-row">
                  <label>Mobile Number</label>
                  <input type="text" v-model="newCustomer.mobile" class="price-input-field" placeholder="Enter mobile">
                </div>
              </div>
              <div class="card-footer">
                <button class="btn-cancel" @click="showNewCustomerModal = false">Cancel</button>
                <button class="btn-add" @click="createAndSelectCustomer">Create & Select</button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="selectedCustomer" class="selected-customer">
          <div class="customer-badge">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
            <span>{{ selectedCustomer.customer_name }}</span>
          </div>
        </div>

        <div class="cart-items-container">
          <div v-if="cartItems.length === 0" class="empty-cart">
            <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
              <circle cx="9" cy="21" r="1" />
              <circle cx="20" cy="21" r="1" />
              <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
            </svg>
            <p>Cart is empty</p>
          </div>

          <div v-else class="cart-items">
            <div v-for="(item, index) in cartItems" :key="index" class="cart-item">

              <div class="cart-item-top">
                <div class="cart-item-image">
                  <img v-if="item.image" :src="item.image" :alt="item.item_name" />
                  <div v-else class="no-image-small">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <rect x="3" y="3" width="18" height="18" rx="2" />
                    </svg>
                  </div>
                </div>

                <div class="cart-item-details-right">
                  <div class="cart-item-header">
                    <div class="cart-text-group">
                      <div class="cart-item-name" :title="item.item_name">{{ item.item_name }}</div>
                      <div class="cart-item-code">{{ item.item_code }}</div>
                    </div>
                    <button @click="removeFromCart(index)" class="remove-btn">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                        stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="3 6 5 6 21 6" />
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                      </svg>
                    </button>
                  </div>

                  <div v-if="item.remarks" class="cart-item-remarks">
                    {{ item.remarks }}
                  </div>
                </div>
              </div>

              <div class="cart-item-footer-wide">
                <div class="quantity-selector-wide">
                  <button @click="decrementQuantity(index)" class="qty-btn">-</button>
                  <input type="number" v-model.number="item.qty" @change="updateItemTotal(index)" class="qty-input"
                    min="1" />
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

        <div class="remarks-section">
          <label class="remarks-label">Remarks</label>
          <textarea v-model="orderRemarks" class="remarks-textarea" rows="2"
            placeholder="Add order remarks..."></textarea>
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

          <button @click="submitOrder" :disabled="cartItems.length === 0 || !selectedCustomer" class="submit-btn">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M5 12h14M12 5l7 7-7 7" />
            </svg>
            Submit & Print
          </button>
        </div>
      </div>
    </div>

    <div v-if="showItemModal" class="modal-overlay" @click.stop>
      <div class="card" @click.stop>

        <div class="card-header">
          <h2>Add to Cart</h2>
          <button class="close-btn" @click="closeItemModal">
            <svg width="12" height="12" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="2.2"
              stroke-linecap="round">
              <line x1="1" y1="1" x2="13" y2="13" />
              <line x1="13" y1="1" x2="1" y2="13" />
            </svg>
          </button>
        </div>

        <div class="product-section">
          <div class="product-image">
            <img v-if="currentItem.image" :src="currentItem.image" :alt="currentItem.item_name"
              style="width:100%; height:100%; object-fit:cover;">
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"
              stroke-linejoin="round">
              <rect x="3" y="3" width="18" height="18" rx="2" />
              <circle cx="8.5" cy="8.5" r="1.5" />
              <path d="m21 15-5-5L5 21" />
            </svg>
          </div>
          <div class="product-info">
            <div class="product-sku">{{ currentItem.jintex_item_codes || currentItem.name }}</div>
            <div class="product-name">{{ currentItem.item_name }}</div>
            <div class="stock-badges">
              <span class="badge badge-green">BLR: {{ formatStock(currentItem.banglore) }}</span>
              <span class="badge badge-amber">AMD: {{ formatStock(currentItem.ahmedabad) }}</span>
            </div>
          </div>
        </div>

        <div class="divider"></div>

        <div class="section">
          <div class="section-label">Price Type</div>
          <div class="price-options">
            <label class="price-option" :class="{ active: modalPriceType === 'dealer' }">
              <input type="radio" v-model="modalPriceType" value="dealer">
              <div class="price-left">
                <div class="radio-outer">
                  <div class="radio-inner"></div>
                </div>
                <span class="price-label">Dealer</span>
              </div>
              <span class="price-value">₹{{ formatAmount(currentItem.dealer) }}</span>
            </label>
            <label class="price-option" :class="{ active: modalPriceType === 'prime' }">
              <input type="radio" v-model="modalPriceType" value="prime">
              <div class="price-left">
                <div class="radio-outer">
                  <div class="radio-inner"></div>
                </div>
                <span class="price-label">Prime</span>
              </div>
              <span class="price-value">₹{{ formatAmount(currentItem.prime) }}</span>
            </label>
            <label class="price-option" :class="{ active: modalPriceType === 'inclusive' }">
              <input type="radio" v-model="modalPriceType" value="inclusive">
              <div class="price-left">
                <div class="radio-outer">
                  <div class="radio-inner"></div>
                </div>
                <span class="price-label">Inclusive</span>
              </div>
              <span class="price-value">₹{{ formatAmount(currentItem.inclusive || 0) }}</span>
            </label>
          </div>
        </div>

        <div class="qty-price-block">
          <div class="qty-price-row">
            <div class="field-group">
              <label>Quantity</label>
              <div class="qty-control">
                <button class="qty-btn" @click="modalQuantity = Math.max(1, modalQuantity - 1)">−</button>
                <input type="number" class="qty-input" v-model.number="modalQuantity" min="1">
                <button class="qty-btn" @click="modalQuantity++">+</button>
              </div>
            </div>
            <div class="field-group">
              <label>Price (₹)</label>
              <input type="number" class="price-input-field" v-model.number="modalPrice" step="0.01">
            </div>
          </div>
        </div>

        <div class="remarks-section">
          <label>Remarks</label>
          <textarea class="remarks-input" v-model="modalRemarks" placeholder="Optional remarks..."></textarea>
        </div>

        <div class="card-footer">
          <div class="total-section">
            <span class="total-label">Total</span>
            <span class="total-value" :style="{ fontSize: totalFontSize }">
              <span class="currency">₹</span>{{ (modalQuantity * modalPrice).toFixed(2) }}
            </span>
          </div>
          <div class="footer-actions">
            <button class="btn-cancel" @click="closeItemModal">Cancel</button>

            <button class="btn-add" :class="{ success: isAddedState }" @click="addToCartFromModal">
              <template v-if="!isAddedState">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                  stroke-linejoin="round">
                  <circle cx="9" cy="21" r="1" />
                  <circle cx="20" cy="21" r="1" />
                  <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
                </svg>
                Add to Cart
              </template>
              <template v-else>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"
                  stroke-linecap="round" stroke-linejoin="round" style="animation: checkPop 0.3s ease-out">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
                Added!
              </template>
            </button>
          </div>
        </div>

      </div>
    </div>
    <div v-if="showMrqModal" class="modal-overlay" @click="closeMrqModal">
      <div class="compact-modal" @click.stop>
        <div class="modal-header">
          <h3>Create Material Request</h3>
          <button @click="closeMrqModal" class="modal-close">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        <div class="modal-body-compact">
          <div class="warning-box" v-if="mrqMessage !== ''">
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
              <input type="number" v-model.number="mrqQty" class="input-compact" min="1" />
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

      gridColumns: 4,
      offset: 0,
      limit: 15,
      hasMore: true,

      // MRQ Logic
      showMrqModal: false,
      mrqItem: null,
      mrqMessage: '',
      mrqQty: 1,
      mrqWarehouse: '',
      warehouses: [],
      isAddedState: false,

      //Customer Creation
      showNewCustomerModal: false,
      newCustomer: {
        name: '',
        mobile: ''
      }
    };
  },

  computed: {
    cartTotal() {
      return this.cartItems.reduce((sum, item) => sum + item.amount, 0);
    },
    totalQuantity() {
      return this.cartItems.reduce((sum, item) => sum + item.qty, 0);
    },
    totalFontSize() {
      const total = (this.modalQuantity * this.modalPrice).toFixed(2);
      const len = total.length;

      if (len > 15) return '14px'; // Very long numbers
      if (len > 10) return '18px'; // Long numbers
      return '24px';               // Standard size
    }
  },

  mounted() {
    this.init();
    document.addEventListener('click', this.handleClickOutside);
    // Hide Frappe's default page header
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

    async createAndSelectCustomer() {
      if (!this.newCustomer.name || !this.newCustomer.mobile) {
        frappe.msgprint('Please fill both Name and Mobile');
        return;
      }

      try {
        const response = await frappe.call({
          method: 'jintex_customization.jintex_management.page.pos.pos.quick_create_customer',
          args: {
            customer_name: this.newCustomer.name,
            mobile_no: this.newCustomer.mobile
          }
        });

        if (response.message) {
          // Select the newly created customer
          this.selectCustomer({
            name: response.message.name,
            customer_name: response.message.customer_name
          });

          // Reset and close
          this.newCustomer = { name: '', mobile: '' };
          this.showNewCustomerModal = false;

          frappe.show_alert({ message: 'Customer created!', indicator: 'green' });
        }
      } catch (error) {
        console.error(error);
      }
    },
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
            // filters: { status: 'Active' },
            fields: ['name'],
            limit_page_length: 0
          }
        });
        if (response.message) {
          this.warehouses = response.message.map(w => w.name);
          const keyword = "Bangalore Warehouse"; // or a variable dynamic value

          this.mrqWarehouse = this.warehouses.find(w =>
            w.toLowerCase().includes(keyword.toLowerCase())
          );
        }
      } catch (error) {
        console.error('Failed to load warehouses:', error);
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

    copyPrice(item, price, event) {
      // Animation Logic from HTML design
      if (event && event.currentTarget) {
        const btn = event.currentTarget;
        btn.classList.add('copied');
        const originalHtml = btn.innerHTML;
        btn.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>';
        setTimeout(() => {
          btn.classList.remove('copied');
          btn.innerHTML = originalHtml;
        }, 1000);
      }

      // Clipboard Logic
      const code = item.jintex_item_codes || item.name;
      const textToCopy = `${code} ${item.item_name} @ ${this.formatAmount(price)}`;

      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(textToCopy).catch((err) => {
          console.error('Async: Could not copy text: ', err);
        });
      } else {
        const textArea = document.createElement("textarea");
        textArea.value = textToCopy;
        textArea.style.position = "fixed";
        textArea.style.left = "-9999px";
        textArea.style.top = "0";
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        try {
          document.execCommand('copy');
        } catch (err) {
          console.error('Fallback: Oops, unable to copy', err);
        }
        document.body.removeChild(textArea);
      }
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
        }, 0.5);

        // Clear cart
        this.cartItems = [];
        this.orderRemarks = '';
        this.selectedCustomer = null;
        this.customerSearch = '';

        const url = `/desk/print/Sales Order/${response.message.name}`;
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
      this.mrqMessage = 'Checking...';

      try {
        const response = await frappe.call({
          method: 'jintex_customization.jintex_management.page.material_request_pag.material_request_pag.check_purchase_material',
          args: {
            product_id: item.name
          }
        });
        if (response.message || 0) {
          this.mrqMessage = "Quantity to be Received: " + (response.message || '0');
        } else {
          this.mrqMessage = '';
        }

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
    },

    openProductDetail(item) {
      const encodedName = encodeURIComponent(item.name);
      const url = `/app/item/${encodedName}`;
      window.open(url, '_blank');
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

      // Animation Logic
      this.isAddedState = true;
      setTimeout(() => {
        this.isAddedState = false;
        frappe.show_alert({
          message: `${cartItem.item_name} added to cart`,
          indicator: 'green'
        }, 0.5);
        this.closeItemModal();

      }, 1000); // Wait 1s for animation before closing
    },

    goToSalesOrders() {
      const url = `/app/sales-order`;
      window.open(url, '_blank');
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
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.jintex-pos {
  /* DESIGN TOKENS */
  --bg-page: #F0F1F5;
  --bg-card: #FFFFFF;
  --bg-elevated: #F7F8FA;
  --border: #E4E6ED;
  --border-hover: #CCCFD9;
  --text-primary: #1A1D2B;
  --text-secondary: #5A5F73;
  --text-muted: #9498AB;
  --accent: #3B5BF5;
  --accent-hover: #2D4CE0;
  --green: #16A362;
  --green-bg: #EDFAF3;
  --green-border: #C5F0DA;
  --green-text: #0E7B4A;
  --red: #E5453E;
  --red-bg: #FEF1F0;
  --red-border: #FACBC9;
  --red-text: #C0322C;
  --radius-sm: 10px;
  --radius-md: 14px;
  --radius-lg: 20px;
  --shadow-card: 0 8px 40px rgba(26, 29, 43, 0.08), 0 1px 3px rgba(26, 29, 43, 0.06);

  height: calc(100vh);
  display: flex;
  flex-direction: column;
  background: var(--bg-page);
  font-family: 'DM Sans', sans-serif;
  color: var(--text-primary);
}

/* Top Bar */
.pos-topbar {
  background: white;
  padding: 0.75rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  z-index: 100;
  border-bottom: 1px solid var(--border);
}

.topbar-left {
  flex-shrink: 0;
}

.pos-brand {
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--accent);
  margin: 0;
}

.topbar-center {
  flex: 1;
  display: flex;
  gap: 1rem;
  align-items: center;
}

.search-container {
  position: relative;
  flex: 1;
  max-width: 400px;
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 0 3rem;
  height: 46px;
  border: 2px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  transition: 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(59, 91, 245, 0.1);
}

.clear-btn {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  width: 28px;
  height: 28px;
  border: none;
  background: var(--bg-elevated);
  border-radius: 6px;
  cursor: pointer;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
}

.topbar-filters {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.topbar-select {
  padding: 0 2rem 0 1rem;
  height: 46px;
  border: 2px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 0.95rem;
  color: var(--text-secondary);
  background: white;
  cursor: pointer;
  min-width: 140px;
  line-height: 44px;
}

.topbar-select:focus {
  outline: none;
  border-color: var(--accent);
}

.grid-toggle {
  display: flex;
  gap: 0.25rem;
  background: var(--bg-elevated);
  padding: 4px;
  border-radius: var(--radius-sm);
  height: 46px;
  align-items: center;
}

.grid-toggle-btn {
  padding: 0 0.75rem;
  height: 100%;
  border: none;
  background: transparent;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-muted);
}

.grid-toggle-btn.active {
  background: white;
  color: var(--accent);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}
.topbar-right {
  display: flex;
  flex-direction: row; /* Ensures horizontal alignment */
  align-items: center;
  gap: 10px;           /* Adds space between the two buttons */
  flex-shrink: 0;      /* Prevents the buttons from squishing */
}
.view-orders-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0 1.25rem;
  height: 46px;
  background: #dbeafe;
  color: #1e40af;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
}

/* Content Grid */
.pos-content {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 0;
  overflow: hidden;
}

.items-section {
  background: var(--bg-page);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.items-grid-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
  padding: 8px;
}

.items-grid {
  display: grid;
  gap: 0.30rem;
}

.items-grid.grid-cols-3 {
  grid-template-columns: repeat(3, 1fr);
}

.items-grid.grid-cols-4 {
  grid-template-columns: repeat(4, 1fr);
}

/* --- NEW ITEM CARD STYLES --- */
.item-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-card);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.item-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(26, 29, 43, 0.12);
}

/* Image Section */
.image-section {
  background: var(--bg-elevated);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  object-fit: contain;
}

.image-section img {
  width: 210px;
  height: 210px;
  object-fit: cover;
  border-radius: var(--radius-sm);
  object-fit: contain;
}

.image-placeholder {
  width: 210px;
  height: 210px;
  background: var(--bg-card);
  border: 2px dashed var(--border);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-placeholder svg {
  color: var(--text-muted);
}

/* Product Info */
.product-info {
  padding: 16px 16px 0;
}

.product-sku {
  font-family: 'JetBrains Mono', monospace;
  font-size: 17px;
  font-weight: 600;
  color: var(--accent);
  margin-bottom: 4px;
  letter-spacing: 0.01em;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
  transition: color 0.15s;
}

.product-sku:hover {
  color: var(--accent-hover);
  text-decoration: underline;
}

.product-name {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.35;
  margin-bottom: 8px;
  letter-spacing: -0.01em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  /* Truncate long names */
}

/* Meta Info */
.meta-list {
  padding: 0 16px 8px;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.meta-row {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.meta-row strong {
  color: var(--text-primary);
  font-weight: 600;
}

.meta-label {
  color: var(--text-muted);
  font-weight: 500;
}

/* Stock Badges */
.stock-section {
  padding: 0 16px 4px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.stock-badge {
  text-align: center;
  padding: 3px 10px;
  border-radius: var(--radius-sm);
  transition: transform 0.15s;
}

.stock-badge:hover {
  transform: translateY(-1px);
}

.stock-badge-green {
  background: var(--green-bg);
  border: 1px solid var(--green-border);
}

.stock-badge-red {
  background: var(--red-bg);
  border: 1px solid var(--red-border);
}

.stock-location {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.stock-count {
  font-size: 15px;
  font-weight: 700;
}

.stock-badge-green .stock-count {
  color: var(--green-text);
}

.stock-badge-red .stock-count {
  color: var(--red-text);
}

/* Transit Info */
.transit-row {
  padding: 2px 16px 7px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.transit-item {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}

.transit-item strong {
  color: var(--text-primary);
  font-weight: 600;
}

/* Divider */
.divider {
  height: 1px;
  background: var(--border);
  margin: 0 16px;
}

.spacer-top {
  margin-top: auto;
}

/* Prices Grid */
.price-row {
  padding: 12px 16px;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 4px;
  text-align: center;
}

.price-col {
  display: flex;
  flex-direction: column;
  gap: 3px;
  padding: 6px 4px;
  border-radius: 8px;
  transition: background 0.15s;
}

.price-col:hover {
  background: var(--bg-elevated);
}

.price-col-label {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted);
}

.price-col-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  letter-spacing: 0.05em;
  user-select: none;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.price-col-masked,
.price-col-actual {
  min-width: 36px;
  text-align: center;
}

.price-col-actual {
  display: none;
}

.price-col:hover .price-col-value .price-col-masked {
  display: none;
}

.price-col:hover .price-col-value .price-col-actual {
  display: inline;
  color: var(--text-primary);
}

.copy-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border: none;
  background: var(--border);
  border-radius: 5px;
  cursor: pointer;
  color: var(--text-muted);
  padding: 0;
  flex-shrink: 0;
  transition: all 0.15s;
  opacity: 0;
  pointer-events: none;
}

.copy-btn:hover {
  background: var(--accent);
  color: #fff;
}

.price-col:hover .copy-btn {
  opacity: 1;
  pointer-events: auto;
}

.copy-btn.copied {
  background: var(--green);
  color: #fff;
}

/* Actions */
.actions {
  padding: 0 16px 16px;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 10px;
}

.btn-cart {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 11px 16px;
  border-radius: var(--radius-sm);
  border: none;
  background: var(--accent);
  color: #fff;
  font-family: 'DM Sans', sans-serif;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  overflow: hidden;
}

.btn-cart::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
  pointer-events: none;
}

.btn-cart:hover {
  background: var(--accent-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(59, 91, 245, 0.25);
}

.btn-cart:active {
  transform: translateY(0);
}

.btn-cart svg {
  width: 18px;
  height: 18px;
}

.btn-mrq {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 11px 20px;
  border-radius: var(--radius-sm);
  border: 1.5px solid var(--red-border);
  background: var(--red-bg);
  color: var(--red-text);
  font-family: 'DM Sans', sans-serif;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  letter-spacing: 0.02em;
}

.btn-mrq:hover {
  background: #FDE4E2;
  border-color: #F5A8A4;
  transform: translateY(-1px);
}

.btn-mrq:active {
  transform: translateY(0);
}

/* --- END ITEM CARD STYLES --- */

/* Cart Section & Modals (Preserved from original but updated to match theme variables) */
.cart-section {
  background: white;
  border-left: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.customer-search {
  position: relative;
  margin: 1rem;
}

.customer-input {
  width: 100%;
  padding: 0.875rem 3rem 0.875rem 3rem;
  border: 2px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 0.95rem;
  transition: all 0.2s;
}

.customer-input:focus {
  outline: none;
  border-color: var(--accent);
}

.clear-customer-btn {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  width: 28px;
  height: 28px;
  border: none;
  background: var(--bg-elevated);
  border-radius: 6px;
  cursor: pointer;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
}


.customer-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 2px solid var(--border);
  border-radius: var(--radius-sm);
  margin-top: 0.5rem;
  max-height: 300px;
  overflow-y: auto;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.customer-option {
  padding: 0.875rem 1rem;
  cursor: pointer;
  transition: all 0.15s;
  border-bottom: 1px solid var(--bg-elevated);
}

.customer-option:hover {
  background: var(--bg-elevated);
}

.customer-name {
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}

.customer-code {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.selected-customer {
  margin: 0 1rem 1rem 1rem;
}

.customer-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #dbeafe;
  color: #1e40af;
  border-radius: var(--radius-sm);
  font-weight: 600;
  font-size: 0.9rem;
}

.cart-items-container {
  flex: 1;
  overflow-y: auto;
  padding: 0 1rem;
}

.empty-cart {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-muted);
}

.empty-cart p {
  margin-top: 1rem;
  color: var(--text-muted);
  font-size: 0.95rem;
}

/* Cart Items Container */
.cart-items {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Main Cart Item Card */
.cart-item {
  background: var(--bg-card);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  /* Stack top and footer */
  overflow: hidden;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

/* Top Section (Image + Details) */
.cart-item-top {
  display: flex;
  gap: 1rem;
  padding: 1rem;
}

.cart-item-image {
  width: 64px;
  height: 64px;
  flex-shrink: 0;
  border-radius: 6px;
  overflow: hidden;
  background: var(--bg-elevated);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border);
}

.cart-item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-image-small {
  color: var(--text-muted);
}

/* Right Side Details */
.cart-item-details-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 0;
  /* Needed for text truncation */
}

.cart-item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}

.cart-text-group {
  flex: 1;
  min-width: 0;
}

.cart-item-name {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.95rem;
  line-height: 1.3;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cart-item-code {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-top: 0.125rem;
  font-family: 'JetBrains Mono', monospace;
}

.remove-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: var(--bg-elevated);
  color: var(--red-text);
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.remove-btn:hover {
  background: var(--red-bg);
  color: var(--red-text);
}

.cart-item-remarks {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-style: italic;
  background: var(--bg-elevated);
  padding: 0.5rem 0.75rem;
  border-radius: 4px;
  border-left: 3px solid var(--accent);
}

/* Wide Footer Section (Below Image) */
.cart-item-footer-wide {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: var(--bg-elevated);
  /* Contrast background for footer */
  border-top: 1px solid var(--border);
  gap: 1rem;
}

/* Wide Quantity Selector */
.quantity-selector-wide {
  display: flex;
  align-items: center;
  flex: 1;
  /* Takes available space */
  height: 36px;
  border: 2px solid var(--border);
  background: white;
  border-radius: 6px;
  overflow: hidden;
}

.quantity-selector-wide:focus-within {
  border-color: var(--accent);
}

/* Reusing qty button/input styles adapted for wide container */
.qty-btn {
  width: 36px;
  height: 100%;
  border: none;
  background: #f8fafc;
  color: var(--text-secondary);
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  border-right: 1px solid var(--border);
}

.qty-btn:last-child {
  border-right: none;
  border-left: 1px solid var(--border);
}

.qty-btn:hover {
  background: #e2e8f0;
  color: var(--text-primary);
}

.qty-input {
  flex: 1;
  width: 100%;
  height: 100%;
  border: none;
  text-align: center;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
  background: white;
  padding: 0;
  -moz-appearance: textfield;
}

.qty-input:focus {
  outline: none;
  background: #fdfdfd;
}

.qty-input::-webkit-outer-spin-button,
.qty-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

/* Price in footer */
.cart-item-price {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0;
  flex-shrink: 0;
}

.price-label {
  font-size: 0.7rem;
  color: var(--text-secondary);
  font-weight: 600;
  text-transform: uppercase;
}

.price-amount {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
  font-family: 'JetBrains Mono', monospace;
}

.remarks-section {
  /* Matches the horizontal margin of qty-price-block (22px) */
  padding: 0 22px 20px;
  width: 100%;
  box-sizing: border-box;
}

.remarks-label {
  display: block;
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.remarks-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  resize: vertical;
  font-family: inherit;
}

.remarks-textarea:focus {
  outline: none;
  border-color: var(--accent);
}

.cart-summary {
  background: white;
  padding: 1.25rem 1rem;
  border-top: 1px solid var(--border);
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  font-size: 0.95rem;
}

.summary-label {
  color: var(--text-secondary);
  font-weight: 500;
}

.summary-value {
  font-weight: 600;
  color: var(--text-primary);
}

.total-row {
  font-size: 1.1rem;
  padding-top: 0.75rem;
  border-top: 2px solid var(--border);
  margin-bottom: 1rem;
}

.total-row .summary-value {
  font-size: 1.25rem;
  color: var(--accent);
}

.submit-btn {
  width: 100%;
  padding: 1rem;
  background: var(--accent);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.submit-btn:hover:not(:disabled) {
  background: var(--accent-hover);
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.3);
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Modal & General */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 2rem;
}

.compact-modal {
  background: white;
  border-radius: var(--radius-lg);
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
}

.modal-header {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.modal-close {
  width: 32px;
  height: 32px;
  border: none;
  background: var(--bg-elevated);
  border-radius: 6px;
  cursor: pointer;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.modal-close:hover {
  background: var(--border);
}

.modal-body-compact {
  padding: 1.25rem;
  overflow-y: auto;
  max-height: calc(90vh - 140px);
}

.modal-item-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.25rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid var(--border);
}

.modal-item-img {
  width: 80px;
  height: 80px;
  flex-shrink: 0;
  border-radius: var(--radius-sm);
  overflow: hidden;
  background: var(--bg-elevated);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-item-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.modal-item-details {
  flex: 1;
}

.modal-item-code {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--accent);
  margin-bottom: 0.25rem;
  font-family: 'JetBrains Mono', monospace;
}

.modal-item-name {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
  line-height: 1.3;
}

.modal-stock-row {
  display: flex;
  gap: 0.5rem;
}

.stock-chip {
  padding: 0.25rem 0.5rem;
  background: #dbeafe;
  color: #1e40af;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.modal-form-compact {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-row label {
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.price-radios-compact {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.radio-compact {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 0.75rem;
  border: 2px solid var(--border);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.radio-compact:hover {
  border-color: var(--accent);
  background: var(--bg-elevated);
}

.radio-compact input[type="radio"] {
  cursor: pointer;
}

.radio-compact span:nth-child(2) {
  flex: 1;
  font-weight: 500;
  color: var(--text-primary);
  font-size: 0.9rem;
}

.radio-price {
  font-weight: 700;
  color: var(--accent);
  font-size: 0.9rem;
}

.input-compact {
  padding: 0 1rem;
  height: 46px;
  border: 2px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 0.95rem;
  font-weight: 600;
}

.input-compact:focus {
  outline: none;
  border-color: var(--accent);
}

.textarea-compact {
  padding: 0.625rem 0.75rem;
  border: 2px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  resize: vertical;
  font-family: inherit;
}

.textarea-compact:focus {
  outline: none;
  border-color: var(--accent);
}

.modal-total-compact {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: var(--bg-elevated);
  border-radius: 6px;
  margin-top: 0.5rem;
}

.modal-total-compact span:first-child {
  font-weight: 600;
  color: var(--text-secondary);
}

.total-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--accent);
}

.modal-footer-compact {
  padding: 1rem 1.25rem;
  border-top: 1px solid var(--border);
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.warning-box {
  background: #fff7ed;
  border: 1px solid #fed7aa;
  color: #c2410c;
  padding: 0.75rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 600;
}

.static-value {
  padding: 0.625rem 0.75rem;
  background: #f1f5f9;
  border-radius: 6px;
  color: #475569;
  font-weight: 600;
}

.btn-secondary-sm {
  padding: 0.625rem 1.25rem;
  background: var(--bg-elevated);
  color: var(--text-secondary);
  border-radius: 6px;
  border: none;
  font-weight: 600;
  cursor: pointer;
}

.btn-secondary-sm:hover {
  background: var(--border);
}

.btn-primary-sm {
  padding: 0.625rem 1.25rem;
  background: var(--accent);
  color: white;
  border-radius: 6px;
  border: none;
  font-weight: 600;
  cursor: pointer;
}

.btn-primary-sm:hover {
  background: var(--accent-hover);
  transform: translateY(-1px);
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--bg-elevated);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.load-more-container {
  padding: 1.5rem;
  text-align: center;
}

.load-more-btn {
  padding: 0.75rem 2rem;
  background: var(--bg-elevated);
  color: var(--text-secondary);
  border: 2px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.load-more-btn:hover {
  background: white;
  border-color: var(--accent);
  color: var(--accent);
}

/* Scrollbar */
.items-grid-container::-webkit-scrollbar,
.cart-items-container::-webkit-scrollbar,
.customer-dropdown::-webkit-scrollbar,
.modal-body-compact::-webkit-scrollbar {
  width: 8px;
}

.items-grid-container::-webkit-scrollbar-track,
.cart-items-container::-webkit-scrollbar-track,
.customer-dropdown::-webkit-scrollbar-track,
.modal-body-compact::-webkit-scrollbar-track {
  background: var(--bg-page);
}

.items-grid-container::-webkit-scrollbar-thumb,
.cart-items-container::-webkit-scrollbar-thumb,
.customer-dropdown::-webkit-scrollbar-thumb,
.modal-body-compact::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

.items-grid-container::-webkit-scrollbar-thumb:hover,
.cart-items-container::-webkit-scrollbar-thumb:hover,
.customer-dropdown::-webkit-scrollbar-thumb:hover,
.modal-body-compact::-webkit-scrollbar-thumb:hover {
  background: var(--text-muted);
}

/* Responsive */
@media (max-width: 1400px) {
  .items-grid.grid-cols-4 {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 1200px) {
  .items-grid.grid-cols-3 {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1024px) {
  .pos-content {
    grid-template-columns: 1fr;
  }

  .cart-section {
    display: none;
  }
}

/* --- NEW ADD TO CART DIALOG STYLES --- */

/* Modal Container (The Card) */
.card {
  width: 100%;
  max-width: 440px;
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-card);
  overflow: hidden;
  animation: cardIn 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  display: flex;
  flex-direction: column;
}

@keyframes cardIn {
  from {
    opacity: 0;
    transform: translateY(12px) scale(0.98);
  }

  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* Header */
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 22px;
  border-bottom: 1px solid var(--border);
}

.card-header h2 {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.01em;
  margin: 0;
}

.close-btn {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  border: none;
  background: #F2F3F7;
  /* Hardcoded bg-input */
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.close-btn:hover {
  background: var(--border);
  color: var(--text-primary);
}

/* Product Section */
.product-section {
  padding: 20px 22px;
  display: flex;
  gap: 16px;
  align-items: center;
  /* Changed from flex-start to center */
}

.product-image {
  width: 68px;
  height: 68px;
  border-radius: var(--radius-md);
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  overflow: hidden;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.product-image svg {
  width: 28px;
  height: 28px;
  color: var(--text-muted);
}

.product-info {
  flex: 1;
  min-width: 0;
}

.product-sku {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  font-weight: 600;
  color: var(--accent);
  margin-bottom: 3px;
}

.product-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.35;
  margin-bottom: 10px;
}

.stock-badges {
  display: flex;
  gap: 6px;
}

.badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 100px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.badge::before {
  content: '';
  width: 5px;
  height: 5px;
  border-radius: 50%;
  flex-shrink: 0;
}

.badge-green {
  background: var(--green-bg);
  color: var(--green-text);
  border: 1px solid var(--green-border);
}

.badge-green::before {
  background: var(--green-text);
}

.badge-amber {
  background: #FFF8EB;
  color: #C47E0A;
  border: 1px solid #FBE5B0;
}

.badge-amber::before {
  background: #C47E0A;
}

/* Price Type Section */
.section {
  padding: 20px 22px;
}

.section-label {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
  margin-bottom: 10px;
}

.price-options {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.price-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 11px 14px;
  border-radius: var(--radius-sm);
  border: 1.5px solid var(--border);
  background: var(--bg-card);
  cursor: pointer;
  transition: all 0.2s;
}

.price-option:hover {
  border-color: var(--border-hover);
}

.price-option.active {
  border-color: var(--accent);
  background: rgba(59, 91, 245, 0.07);
}

.price-option input[type="radio"] {
  display: none;
}

.radio-outer {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid var(--border-hover);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s;
}

.price-option.active .radio-outer {
  border-color: var(--accent);
}

.radio-inner {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent);
  transform: scale(0);
  transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.price-option.active .radio-inner {
  transform: scale(1);
}

.price-left {
  display: flex;
  align-items: center;
  gap: 11px;
}

.price-option .price-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
}

.price-option.active .price-label {
  color: var(--text-primary);
  font-weight: 600;
}

.price-option .price-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-muted);
}

.price-option.active .price-value {
  color: var(--text-primary);
}

/* Qty & Price Block */
.qty-price-block {
  margin: 0 22px 20px;
  background: #F0F9F4;
  border: 1px solid #D8F0E2;
  border-radius: var(--radius-md);
  padding: 16px;
}

.qty-price-row {
  display: grid;
  grid-template-columns: 7fr 3fr;
  gap: 14px;
}

.field-group label {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
  margin-bottom: 8px;
  display: block;
}

.qty-control {
  display: flex;
  align-items: center;
  border: 1.5px solid var(--border);
  border-radius: var(--radius-sm);
  background: #FFFFFF;
  overflow: hidden;
  height: 44px;
  transition: border-color 0.2s;
}

.qty-control:focus-within {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(59, 91, 245, 0.07);
}

.qty-btn {
  width: 40px;
  height: 100%;
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
  user-select: none;
}

.qty-btn:hover {
  background: #F2F3F7;
  color: var(--text-primary);
}

.qty-input {
  flex: 1;
  height: 100%;
  border: none;
  border-left: 1px solid var(--border);
  border-right: 1px solid var(--border);
  background: #FFF;
  color: var(--text-primary);
  font-family: 'JetBrains Mono', monospace;
  font-size: 15px;
  font-weight: 600;
  text-align: center;
  outline: none;
}

.price-input-field {
  width: 100%;
  height: 44px;
  border: 1.5px solid var(--border);
  border-radius: var(--radius-sm);
  background: #FFFFFF;
  color: var(--text-primary);
  font-family: 'JetBrains Mono', monospace;
  font-size: 15px;
  font-weight: 600;
  padding: 0 14px;
  outline: none;
  transition: all 0.2s;
}

.price-input-field:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(59, 91, 245, 0.07);
}

/* Remarks */
.remarks-section {
  padding: 0 22px 20px;
}

.remarks-section label {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
  margin-bottom: 8px;
  display: block;
}

/* Ensure the textarea fills the container */
.remarks-input {
  width: 100%;
  height: 68px;
  border: 1.5px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--bg-card);
  color: var(--text-primary);
  font-family: 'DM Sans', sans-serif;
  font-size: 14px;
  padding: 12px 14px;
  outline: none;
  resize: none;
  transition: all 0.2s;
  box-sizing: border-box;
  /* Ensures padding doesn't expand width */
}

.remarks-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(59, 91, 245, 0.07);
}

/* Footer */
.card-footer {
  padding: 16px 22px;
  border-top: 1px solid var(--border);
  background: var(--bg-elevated);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  /* Adds safe space between total and buttons */
}

/* Total Section: Allow it to take available space but truncate if too long */
.total-section {
  display: flex;
  flex-direction: column;
  min-width: 0;
  /* Critical for truncation to work in flexbox */
  flex: 1;
  /* Take up remaining space */
}

.total-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
  margin-bottom: 1px;
}

/* Total Value: Handle large numbers gracefully */
.total-value {
  font-family: 'JetBrains Mono', monospace;
  /* Font size will now be handled by inline style */
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.02em;

  /* Remove truncation to allow font scaling to work */
  white-space: nowrap;
  /* overflow: hidden;  <-- Removed */
  /* text-overflow: ellipsis; <-- Removed */
  transition: font-size 0.2s ease;
}

.total-value .currency {
  font-size: 16px;
  color: var(--text-secondary);
  margin-right: 1px;
}

/* Footer Actions: Prevent shrinking */
.footer-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
  /* Ensures buttons never squish or move */
}

.btn-cancel {
  padding: 10px 18px;
  border-radius: var(--radius-sm);
  border: 1.5px solid var(--border);
  background: var(--bg-card);
  color: var(--text-secondary);
  font-family: 'DM Sans', sans-serif;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel:hover {
  border-color: var(--border-hover);
  color: var(--text-primary);
}

.btn-add {
  padding: 10px 22px;
  border-radius: var(--radius-sm);
  border: none;
  background: var(--accent);
  color: #fff;
  font-family: 'DM Sans', sans-serif;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-add:hover {
  background: var(--accent-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(59, 91, 245, 0.25);
}

.btn-add:active {
  transform: translateY(0);
}

.btn-add svg {
  width: 16px;
  height: 16px;
}

.btn-add.success {
  background: var(--green);
  pointer-events: none;
}

@keyframes checkPop {
  0% {
    transform: scale(0);
  }

  60% {
    transform: scale(1.2);
  }

  100% {
    transform: scale(1);
  }
}
</style>