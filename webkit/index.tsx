// @ts-ignore
import { callable } from '@steambrew/webkit';

const receiveFrontendMethod = callable<[{ message: string; status: boolean; count: number }], boolean>('Backend.receive_frontend_message');

export default async function WebkitMain() {
		// check URL
		if (!location.href.startsWith("https://store.steampowered.com/app/")) return;

		// avoid duplicates
		if (document.getElementById("add-app-to-library-btn")) return;

		// create button
		const btn = document.createElement("button");
		btn.id = "add-app-to-library-btn";
		btn.textContent = "Add app to library";
		btn.style.cssText = `
		cursor:pointer; border:none; border-radius:8px; padding:10px 14px;
		font-weight:600; font-size:14px; line-height:1;
		background:#1999ff; color:#fff; box-shadow:0 2px 6px rgba(0,0,0,.25);
	  `;

		// click handler
		btn.addEventListener("click", async () => {
			try {
				const success = await receiveFrontendMethod({
					message: window.location.href,
					status: true,
					count: 69,
				});
				console.log("Request finished:", success);
			} catch (err) {
				console.error("Error:", err);
			}
		});

		// insert button at top of page
		document.body.prepend(btn);
}
