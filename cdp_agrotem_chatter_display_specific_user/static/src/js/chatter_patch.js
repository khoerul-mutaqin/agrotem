/** @odoo-module **/

import { useEffect } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";
import { FormController } from '@web/views/form/form_controller';
import { jsonrpc } from "@web/core/network/rpc_service";
import { onWillStart } from "@odoo/owl";

patch(FormController.prototype, {
    setup() {
        super.setup();
        this.forceBottom = false;

        onWillStart(async () => {
            const result = await jsonrpc("/web/dataset/call_kw", {
                model: "res.users",
                method: "read",
                args: [[session.uid], ["has_smaller_chatter"]],
                kwargs: {},
            });

            if (result && result.length > 0) {
                this.forceBottom = result[0].has_smaller_chatter;
            }
        });

        useEffect(() => {
            this.configureChatterPosition();
        });
    },

    configureChatterPosition() {
        const self = this;
        const $form = $(".o_form_view:not(.o_modal)");
        if (!$form.length) return;
    
        if ($form.length === 1) {
            const $sheet = $form.find("div.o_form_sheet_bg");
            const $chatterarea = $form.find("div.o-mail-Form-chatter");
            const $formeditbale = $form.find("div.o_form_renderer");
            const $formcontainer = $form.find("div.o_form_view_container");
            const $formrenderer = $form.find("div.o_form_renderer");
    
            if ($sheet.length && $chatterarea.length && $sheet.has($chatterarea).length) {
                $chatterarea.insertAfter($sheet);
            }
    
            $form.removeClass("o-main-form o_xxl_form_view h-120");
            $formeditbale.removeClass("h-100 flex-nowrap flex-column");
            $chatterarea.removeClass("o-aside o-bottom");
            if (this.forceBottom) {
                $form.addClass("o-main-form o_chatter_at_bottom");
                $formeditbale.removeClass("h-100 flex-nowrap").addClass("flex-column");
                $chatterarea.addClass("o-bottom").removeClass("o-aside");
            } else {
                $form.addClass("o_chatter_small_side");
                $chatterarea.addClass("o-aside").removeClass("o-bottom");
                if (window.innerWidth > 1920 && window.innerWidth <= 3400) {
                    console.log("[ODOO LAYOUT] ULTRAWIDE MODE");                    
                    const chatterWidth = 600;

                    const screenWidth = window.innerWidth;
                    const availableWidth = screenWidth - chatterWidth;
                    const sheetMaxWidth = Math.min(availableWidth, 1920);
                    $formrenderer.attr('style', 'flex: 1 1 auto !important; width: 90% !important; max-width: 90% !important; padding: 0 !important;');
                    
                    $sheet.attr('style', 'width: 100% !important; max-width: 100% !important; margin: 0 !important;');
                    
                    // $sheet.find(".o_form_sheet").attr('style', 'width: 2800px !important; max-width: 2800px !important; margin: 0 auto !important; border-right: 1px solid #dee2e6 !important;');
                    $sheet.find(".o_form_sheet").attr('style', `
                        width: ${sheetMaxWidth}px !important;
                        max-width: ${sheetMaxWidth}px !important;
                        margin: 0 auto !important;
                        border-right: 1px solid #dee2e6 !important;
                    `);

                    $chatterarea.css({
                        flex: "0 0 600px",
                        width: "600px",
                        maxWidth: "600px",
                        minWidth: "600px",
                        overflowX: "hidden",

                        height: "calc(100vh - 60px)",
                        overflowY: "auto",
                        position: "sticky",
                        top: "0"
                    });
                    
                    $chatterarea.find(".o-mail-Chatter").css("overflow-x", "hidden");
                    $chatterarea.find(".o-mail-Chatter-topbar").css({"display": "flex", "flex-wrap": "wrap"});

                } else if (window.innerWidth > 3400) {
                    console.log("[ODOO LAYOUT] SUPER ULTRAWIDE MODE");
                    $formrenderer.attr('style', 'flex: 1 1 auto !important; width: 90% !important; max-width: 90% !important; padding: 0 !important;');
                    
                    $sheet.attr('style', 'width: 100% !important; max-width: 100% !important; margin: 0 !important;');
                    
                    $sheet.find(".o_form_sheet").attr('style', 'width: 2800px !important; max-width: 2800px !important; margin: 0 auto !important; border-right: 1px solid #dee2e6 !important;');

                    $chatterarea.css({
                        flex: "0 0 600px",
                        width: "600px",
                        maxWidth: "600px",
                        minWidth: "600px",
                        overflowX: "hidden",

                        height: "calc(100vh - 60px)",
                        overflowY: "auto",
                        position: "sticky",
                        top: "0"
                    });
                    
                    $chatterarea.find(".o-mail-Chatter").css("overflow-x", "hidden");
                    $chatterarea.find(".o-mail-Chatter-topbar").css({"display": "flex", "flex-wrap": "wrap"});

                } else {
                    console.log("Standard Screen Detected: Using Normal Sidebar");
                    const screenWidth = window.innerWidth;
                    const screenHeight = window.innerHeight;
                    const chatterWidth = 600;
                    const availableWidth = screenWidth - chatterWidth;
                    // Target size
                    const baseWidth = 1920;
                    const baseHeight = 1080;

                    // Count zoom factor based on available width and height
                    const zoomX = availableWidth / baseWidth;
                    const zoomY = screenHeight / baseHeight;

                    const autoZoom = Math.min(1, zoomX, zoomY);

                    // Limit minimum zoom
                    const finalZoom = Math.max(0.65, autoZoom);

                    // CSS `zoom` scales the element's own width too: an element with
                    // `width: W; zoom: z` is drawn W * z px wide. So:
                    //  - the chatter really takes chatterWidth * zoom px on screen
                    //  - the renderer needs width / zoom to fill the remaining space
                    // Before, the sheet (availableWidth / zoom) was wider than the
                    // renderer (availableWidth * zoom) -> right part of order lines hidden.
                    const visibleFormWidth = screenWidth - chatterWidth * finalZoom;
                    const rendererCssWidth = Math.floor(visibleFormWidth / finalZoom);
                    const sheetMaxWidth = Math.min(rendererCssWidth, 1920);

                    // FORM RENDERER
                    $formrenderer.attr("style", `
                        flex: 1 1 auto !important;
                        width: ${rendererCssWidth}px !important;
                        max-width: ${rendererCssWidth}px !important;
                        min-width: 0 !important;
                        padding: 0 !important;
                        zoom: ${finalZoom} !important;
                    `);

                    // SHEET CONTAINER
                    $sheet.attr("style", `
                        width: 100% !important;
                        max-width: 100% !important;
                        margin: 0 !important;
                    `);

                    // FORM SHEET
                    $sheet.find(".o_form_sheet").attr("style", `
                        width: ${sheetMaxWidth}px !important;
                        max-width: ${sheetMaxWidth}px !important;
                        margin: 0 auto !important;
                        border-right: 1px solid #dee2e6 !important;
                    `);

                    // CHATTER
                    $chatterarea.css({
                        flex: "0 0 600px",
                        width: "600px",
                        maxWidth: "600px",
                        minWidth: "600px",
                        height: "calc(100vh - 60px)",
                        overflowX: "hidden",
                        overflowY: "auto",
                        position: "sticky",
                        top: "0",
                        zoom: finalZoom
                    });

                    // CHATTER CONTENT
                    $chatterarea.find(".o-mail-Chatter").css({
                        overflowX: "hidden"
                    });

                    // LOG
                    console.table({
                        Mode: "AUTO ZOOM TO FIT",
                        Screen: `${screenWidth} x ${screenHeight}`,
                        AvailableWidth: availableWidth,
                        Zoom: `${(finalZoom * 100).toFixed(1)}%`,
                        ChatterWidth: chatterWidth
                    });



                }

            }
        }
    },
});