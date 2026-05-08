frappe.ui.form.on("Freight Settlement", {
    refresh(frm) {
        if (frm.doc.gross_margin !== undefined) {
            const color = frm.doc.gross_margin >= 0 ? "green" : "red";
            frm.page.set_indicator(
                `Margin: ₹${frm.doc.gross_margin?.toFixed(2)} (${frm.doc.margin_percent?.toFixed(1)}%)`,
                color
            );
        }
    }
});

frappe.ui.form.on("Freight Settlement Revenue", {
    net_revenue(frm) { frm.trigger("recalc"); },
    revenue_lines_remove(frm) { frm.trigger("recalc"); }
});

frappe.ui.form.on("Freight Settlement Cost", {
    amount(frm) { frm.trigger("recalc"); },
    cost_lines_remove(frm) { frm.trigger("recalc"); }
});

frappe.ui.form.on("Freight Settlement", {
    recalc(frm) {
        const rev = (frm.doc.revenue_lines || []).reduce((s, r) => s + (r.net_revenue || 0), 0);
        const cost = (frm.doc.cost_lines || []).reduce((s, r) => s + (r.amount || 0), 0);
        frm.set_value("total_revenue", rev);
        frm.set_value("total_cost", cost);
        frm.set_value("gross_margin", rev - cost);
        frm.set_value("margin_percent", rev > 0 ? ((rev - cost) / rev * 100) : 0);
    }
});
