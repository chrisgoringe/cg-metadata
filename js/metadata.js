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
			if (nodeData.name.substring(0,10) === "Set Widget" || 
			    nodeData.name === "Send Metadata to Widgets") {
				const onExecuted = nodeType.prototype.onExecuted;
				nodeType.prototype.onExecuted = function (message) {
					onExecuted?.apply(this, arguments);
					message.updates.forEach(update => {
						var node_id = parseInt(update[0]);
						var widget_name = update[1];
						var text = update[2];
						var widget = this.graph._nodes_by_id[node_id]?.widgets.find((w) => w.name===widget_name);
						if (widget) { 
							widget.value = text; 
							this.graph._nodes_by_id[node_id].onResize?.(this.size);
						} else { console.log("cg.customnodes.SendText - Widget "+widget_name+" not found")}
					});
				};
			}
		},
	});
}

