import { createApp } from 'vue';
import POS from './POS.vue';

class POSUI {
    constructor({ wrapper, page }) {
        this.$wrapper = $(wrapper);
        this.page = page;
        this.app = null;
        this.init();
    }

    init() {
        // Mount Vue app
        this.app = createApp(POS, {
            page: this.page
        });
        this.app.mount(this.$wrapper.get(0));
    }

    destroy() {
        if (this.app) {
            this.app.unmount();
            this.app = null;
        }
    }
}

// Expose to global namespace
frappe.provide("pos.ui");
pos.ui.POSUI = POSUI;

export default POSUI;