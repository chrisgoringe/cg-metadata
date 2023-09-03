import { app } from "../../../scripts/app.js";
import { ComfyWidgets } from "../../../scripts/widgets.js";

app.registerExtension({
	name: "cg.SendText",
	async beforeRegisterNodeDef(nodeType, nodeData, app) {
		if (nodeData.name === "Set Widget Value" || nodeData.name === "Set Widget from Metadata") {
			const onExecuted = nodeType.prototype.onExecuted;
			nodeType.prototype.onExecuted = function (message) {
				onExecuted?.apply(this, arguments);
                const node_index = parseInt(message.node_id.join(''));
                const widget_name = message.widget_name.join('');
				const widget_index = this.graph._nodes_by_id[node_index].widgets.findIndex((w) => w.name===widget_name);
				if (node_index>=0 && widget_index>=0) {
					this.graph._nodes_by_id[node_index].widgets[widget_index].value = message.text.join('');
				}
			};
		}
	},
});

app.registerExtension({
	name: "cg.ShowTextMetadata",
	async beforeRegisterNodeDef(nodeType, nodeData, app) {
		if (nodeData.output_name.findIndex((n) => n==="text_displayed") >= 0) {
			const onExecuted = nodeType.prototype.onExecuted;
			nodeType.prototype.onExecuted = function (message) {
				onExecuted?.apply(this, arguments);

				if (this.widgets) {
					const pos = this.widgets.findIndex((w) => w.name === "text");
					if (pos !== -1) {
						for (let i = pos; i < this.widgets.length; i++) {
							this.widgets[i].onRemove?.();
						}
						this.widgets.length = pos;
					}
				}
				const w = ComfyWidgets["STRING"](this, "text", ["STRING", { multiline: true }], app).widget;
				w.inputEl.readOnly = true;
				w.inputEl.style.opacity = 0.6;
				w.value = message.text_displayed.join('');

				this.onResize?.(this.size);
			};
			nodeType.prototype.onExecutionStart = function () {
				if (this.widgets) {
					const pos = this.widgets.findIndex((w) => w.name === "text");
					if (pos !== -1) {
						this.widgets[pos].value = '';
						this.onResize?.(this.size);
					}
				}
			};
		}
	},
});