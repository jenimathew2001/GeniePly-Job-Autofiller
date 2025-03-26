// chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
//     if (message.action === "extractFormFields") {
//         console.log("📥 Message received: Extracting form fields...");

//         let formStructure = extractFormFields();
//         sendResponse({ formStructure }); // ✅ Ensure response is sent
//         return true; // ✅ Keeps the message channel open for async responses
//     }

//     if (message.action === "autofillForm") {
//         console.log("📥 Message received: Autofilling form...");
//         autofillDynamicForm(message.formFields, message.profileData);
//         sendResponse({ success: true });
//     }
// });

// // Function to extract form fields
// function extractFormFields() {
//     console.log("🔍 Extracting form fields...");

//     const inputs = document.querySelectorAll("input, textarea, select");
//     let formStructure = [];

//     inputs.forEach(field => {
//         let label = "";
//         let parent = field.closest("label") || field.previousElementSibling;
//         if (parent && parent.tagName === "LABEL") {
//             label = parent.innerText.trim();
//         }

//         formStructure.push({
//             name: field.name || field.id || "",
//             label: label || field.placeholder || "",
//             type: field.tagName.toLowerCase(),
//             fieldType: field.type || "",
//         });
//     });

//     console.log("📌 Extracted Form Structure:", formStructure);
//     return formStructure;
// }
