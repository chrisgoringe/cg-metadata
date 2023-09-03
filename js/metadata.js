import { app } from "../../../scripts/app.js";

const version = 1;
const name = "cg.customnodes.SendText";
const index = app.extensions.findIndex((ext) => ext.name === name);
var install = true;
if (index>=0) {
	const installed = app.extensions[index].version;
	if (installed >= version) { install = false; }
	else { app.extensions.splice(index,1); }
}

if (install) {
	app.registerExtension({
		name: name,
		version: version,
		async beforeRegisterNodeDef(nodeType, nodeData, app) {
			if (nodeData.name === "Set Widget Value" || nodeData.name === "Set Widget from Metadata") {
				const onExecuted = nodeType.prototype.onExecuted;
				nodeType.prototype.onExecuted = function (message) {
					onExecuted?.apply(this, arguments);
					const widget_name = message.widget_name?.join('');
					const text = message.text?.join('')
					const node_id = parseInt(message.node_id?.join(''))
					if (widget_name && text && node_id>=0) {
						const widget = this.graph._nodes_by_id[node_index]?.widgets.find((w) => w.name===widget_name);
						if (widget) { widget.value = text; } else { console.log("cg.customnodes.SendText - Widget "+widget_name+" not found")}
					} else { console.log("cg.customnodes.SendText - Something missing")}
				};
			}
		},
	});
}

