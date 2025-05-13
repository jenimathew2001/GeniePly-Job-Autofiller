document.addEventListener("DOMContentLoaded", function () {
    const loginSection = document.getElementById("login-section");
    const uploadSection = document.getElementById("upload-section");
    const passwordSection = document.getElementById("password-section");
    const newPasswordSection = document.getElementById("new-password-section");
    const emailInput = document.getElementById("email");
    const passwordInput = document.getElementById("password");
    const newpasswordInput = document.getElementById("newpassword");
    const startButton = document.getElementById("start-button");
    const loginButton = document.getElementById("login-button");
    const signinButton = document.getElementById("signin-button");

    let storedPassword = null; // Variable to store password temporarily
    let enteredEmail = null; // Store email for new user creation

    startButton.addEventListener("click", async function () {
        const email = emailInput.value.trim();
        if (!email) {
            alert("Please enter an email.");
            return;
        }

        try {
            const response = await fetch("https://genieply.onrender.com/check-user", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ email })
            });

            const data = await response.json();
            if (response.ok) {
                // Store the retrieved password
                storedPassword = data.password;
                enteredEmail = email;
                

                // Hide login section, show password section
                loginSection.classList.add("hidden");
                passwordSection.classList.remove("hidden");
            } else {
                // If user not found, move to new password section
                enteredEmail = email; // Store email for creating new user
                loginSection.classList.add("hidden");
                newPasswordSection.classList.remove("hidden");
            }
        } catch (error) {
            console.error("Error:", error);
            alert("Failed to check user: " + error.message);
        }
    });

    loginButton.addEventListener("click", function () {
        const enteredPassword = passwordInput.value.trim();
        if (!enteredPassword) {
            alert("Please enter your password.");
            return;
        }

        if (enteredPassword === storedPassword) {
            // Correct password: Hide password section, show upload section
            sessionStorage.setItem("enteredEmail", enteredEmail);
            console.log("enteredEmail", enteredEmail)

            passwordSection.classList.add("hidden");
            uploadSection.classList.remove("hidden");
        } else {
            alert("Incorrect password. Please try again.");
        }
    });

    signinButton.addEventListener("click", async function () {
        const newPassword = newpasswordInput.value.trim();
        if (!newPassword) {
            alert("Please enter a password.");
            return;
        }

        try {
            const response = await fetch("https://genieply.onrender.com/create-user", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    email: enteredEmail,
                    password: newPassword
                })
            });

            const data = await response.json();
            if (response.ok) {
                alert("Account created successfully! Please log in.");
                newPasswordSection.classList.add("hidden");
                loginSection.classList.remove("hidden");
            } else {
                alert(data.error || "Failed to create user.");
            }
        } catch (error) {
            console.error("Error:", error);
            alert("Error creating account: " + error.message);
        }
    });



    document.getElementById("cv-upload").addEventListener("change", async function () {
        const file = this.files[0];
        if (!file) return;
        console.log('I am in cv upload',enteredEmail)

        document.getElementById("upload-section").classList.add("hidden");
        document.getElementById("loading").style.display = "block";

        const formData = new FormData();
        formData.append("file", file);
        formData.append("email", enteredEmail);
        console.log('formData', formData)

        try {
            const response = await fetch("https://genieply.onrender.com/upload", {
                method: "POST",
                body: formData
            });
            console.log('response',response)

            const responseText = await response.text();
            console.log('responseText',responseText)
            try {
                const responsejson = JSON.parse(responseText);
                console.log('dataaaaaaaaaaaa',responsejson.data)
                console.log('dataaaaaaaaaaaa data.name',responsejson.data.name)
                if (!response.ok) throw new Error(responsejson.data.error || "Unknown error");

                document.getElementById("loading").style.display = "none";
                document.getElementById("profile-section").classList.remove("hidden");

                // Fill profile fields
                console.log('data.contact?.email',responsejson.data.contact?.email,'enteredEmail',enteredEmail)
                console.log(document.getElementById("email")); 

                document.getElementById("name").value = responsejson.data.name || "";
                document.getElementById("profile-email").value = responsejson.data.contact?.email || enteredEmail ;
                document.getElementById("phone").value = responsejson.data.contact?.phone || "N/A";
                document.getElementById("location").value = responsejson.data.contact?.location || "";

                // Populate Education
                const eduList = document.getElementById("education-list");
                eduList.innerHTML = ""; // Clear duplicates
                if (responsejson.data.education && responsejson.data.education.length > 0) {
                    responsejson.data.education.forEach(edu => {
                        const div = document.createElement("div");
                        div.classList.add("education-item");
                        div.innerHTML = `
                            <label>Degree:</label>
                            <input type="text" value="${edu.degree}" disabled>

                            <label>Institution:</label>
                            <input type="text" value="${edu.institution}" disabled>

                            <label>Location:</label>
                            <input type="text" value="${edu.location}" disabled>

                            <label>Grade:</label>
                            <input type="text" value="${edu.grade || "N/A"}" disabled>

                            <label>Year:</label>
                            <input type="text" value="${edu.year}" disabled>
                    `   ;
                        eduList.appendChild(div);
                    });
                } else {
                    eduList.innerHTML += "<p>No education details found.</p>";
                }

                // Populate Experience
                const expList = document.getElementById("experience-list");
                expList.innerHTML = ""; // Clear duplicates
                if (responsejson.data.experience && responsejson.data.experience.length > 0) {
                    responsejson.data.experience.forEach(exp => {
                        const div = document.createElement("div");
                        div.classList.add("experience-item");
                        div.innerHTML = `
                            <label>Title:</label>
                            <input type="text" value="${exp.title}" disabled>

                            <label>Company:</label>
                            <input type="text" value="${exp.company}" disabled>

                            <label>Location:</label>
                            <input type="text" value="${exp.location}" disabled>

                            <label>Year:</label>
                            <input type="text" value="${exp.year}" disabled>

                            <label>Responsibilities:</label>
                            <textarea disabled>${exp.responsibilities.join("\n")}</textarea>
                    `   ;
                        expList.appendChild(div);
                    });
                } else {
                    expList.innerHTML += "<p>No experience details found.</p>";
                }

            } catch (jsonError) {
                console.error("JSON Parsing Error:", jsonError);
            }

        } catch (error) {
            console.error("Error:", error);
            alert("Failed to upload CV: " + error.message);
            document.getElementById("loading").style.display = "none";
            document.getElementById("upload-section").classList.remove("hidden");
        }
    });

    document.getElementById("view-profile-button").addEventListener("click", async function () {
        if (!enteredEmail) {
            alert("No profile found. Please log in first.");
            return;
        }
    
        try {
            const response = await fetch(`https://genieply.onrender.com/users/${enteredEmail}`);
            if (!response.ok) {
                throw new Error("Profile not found.");
            }
    
            
            const data = await response.json();
            console.log('!!!!!view button data',data)
            // Check if the profile contains more than just login credentials
            if (!data.cv_json || Object.keys(data.cv_json).length === 0) {
                alert("Please upload a CV or manually fill in your profile.");
                return;
            }

            document.getElementById("upload-section").classList.add("hidden");

            const profileData = data.cv_json; // Accessing the second object
            console.log('!!!!!view button data data.cv_json',data.cv_json['name'])
            console.log('!!!!!view button data data[cv_json]',data['cv_json']['name'])

    
            // Display Profile Section
            document.getElementById("profile-section").classList.remove("hidden");
    
            // Fill Profile Fields
            document.getElementById("name").value = profileData.name || "";
            document.getElementById("profile-email").value = profileData.contact?.email || enteredEmail;
            document.getElementById("phone").value = profileData.contact?.phone || "N/A";
            document.getElementById("location").value = profileData.contact?.location || "N/A";
    
            // Populate Education
            const eduList = document.getElementById("education-list");
            eduList.innerHTML = ""; 
            if (profileData.education && profileData.education.length > 0) {
                profileData.education.forEach(edu => {
                    const div = document.createElement("div");
                    div.classList.add("education-item");
                    div.innerHTML = `
                        <label>Degree:</label>
                        <input type="text" value="${edu.degree}" disabled>
    
                        <label>Institution:</label>
                        <input type="text" value="${edu.institution}" disabled>
    
                        <label>Location:</label>
                        <input type="text" value="${edu.location}" disabled>
    
                        <label>Grade:</label>
                        <input type="text" value="${edu.grade || "N/A"}" disabled>
    
                        <label>Year:</label>
                        <input type="text" value="${edu.year}" disabled>
                    `;
                    eduList.appendChild(div);
                });
            } else {
                eduList.innerHTML += "<p>No education details found.</p>";
            }
    
            // Populate Experience
            const expList = document.getElementById("experience-list");
            expList.innerHTML = ""; 
            if (profileData.experience && profileData.experience.length > 0) {
                profileData.experience.forEach(exp => {
                    const div = document.createElement("div");
                    div.classList.add("experience-item");
                    div.innerHTML = `
                        <label>Title:</label>
                        <input type="text" value="${exp.title}" disabled>
    
                        <label>Company:</label>
                        <input type="text" value="${exp.company}" disabled>
    
                        <label>Location:</label>
                        <input type="text" value="${exp.location}" disabled>
    
                        <label>Year:</label>
                        <input type="text" value="${exp.year}" disabled>
    
                        <label>Responsibilities:</label>
                        <textarea disabled>${exp.responsibilities.join("\n")}</textarea>
                    `;
                    expList.appendChild(div);
                });
            } else {
                expList.innerHTML += "<p>No experience details found.</p>";
            }
    
        } catch (error) {
            console.error("Error:", error);
            alert("Failed to load profile: " + error.message);
        }
    });



    document.getElementById("autofill-button").addEventListener("click", function () {
        console.log("🔹 Autofill button clicked!");

        // Show loading, hide upload
        document.getElementById("upload-section").classList.add("hidden");
        document.getElementById("autofilling").style.display = "block";
    
        chrome.tabs.query({ active: true, currentWindow: true }, async function (tabs) {
            if (!tabs[0]) {
                console.error("❌ No active tab found.");
                return;
            }
    
            const tabId = tabs[0].id;

            try{
            const filledSelectors = new Set();
            const sectionSelectors = new Set();
            let loopCounter = 0;
            const maxLoops = 5;
    
            // Fetch user profile once
            const profileResponse = await fetch(`https://genieply.onrender.com/users/${enteredEmail}`);
            const profileData = await profileResponse.json();
    
            if (!profileData.cv_json || Object.keys(profileData.cv_json).length === 0) {
                alert("Please upload a CV or manually fill in your profile.");
                return;
            }

            const sectionContext = {
                experienceCount: {
                                    profile : profileData.cv_json?.experience?.length || 0,
                                    clicked : 0
                                },
                educationCount: {
                                    profile : profileData.cv_json?.education?.length || 0,
                                    clicked : 0
                                },
                certificationCount: {
                                    profile : profileData.cv_json?.certifications?.length || 0,
                                    clicked : 0
                                }
            };

            console.log('section count',sectionContext)
    
            console.log("✅ Loaded Profile:", profileData);
    
            while (loopCounter < maxLoops) {
                console.log(`🔁 Loop #${loopCounter + 1}`);
                loopCounter++;
    
                // 1. Extract Fields
                const extractionResults = await chrome.scripting.executeScript({
                    target: { tabId },
                    function: extractFormFieldsDirectly
                });

                console.log("✅EXTRACTED FIELDS", extractionResults)
    
                let extractedFields = extractionResults?.[0]?.result || [];
    
                // 2. Filter Unwanted Fields
                extractedFields = extractedFields.filter(field => {
                    const label = field.label?.toLowerCase() || "";
                    const name = field.name?.toLowerCase() || "";
                    const idlower = field.id?.toLowerCase() || "";
    
                    return (
                        (field.id || field.name || field.label) &&
                        field.fieldType !== "hidden" &&
                        !(
                            label.includes("save") ||
                            label.includes("cookie") ||
                            label.includes("change") ||
                            label.includes("delete") ||
                            label.includes("back") ||
                            label.includes("switch") ||
                            label.includes("settings") ||
                            label.includes("menu") ||
                            label.includes("account") ||
                            label.includes("language") ||
                            label.includes("submit") ||
                            label.includes("back") ||
                            label.includes("careers page") ||
                            label.includes("search") ||
                            label.includes("alert") ||
                            label.includes("sign") ||
                            label.includes("log out") ||
                            label.includes("english") ||
                            label.includes("candidate home") ||
                            name.includes("vendor") ||
                            name.includes("chkbox") ||
                            idlower.includes("language") ||
                            idlower.includes("settings")||
                            idlower.includes("accountselector")
                        )
                    );
                });

                console.log("✅UNFORMATTED EXTRACTEDFIELDS", extractedFields);
    
                // 3. Format Fields
                extractedFields = extractedFields.map(field => {
                    const fieldType = field.fieldType?.toLowerCase() || "";
                    const actionType = ["text", "textarea", "email", "tel", "number", "password", "url"].includes(fieldType)
                        ? "type"
                        : ["radio", "checkbox"].includes(fieldType)
                        ? "select"
                        : ["submit", "button"].includes(fieldType)
                        ? "click"
                        : "type";
    
                    const selector =
                        field.id ? `#${field.id}` :
                        field.name ? `[name="${field.name}"]` :
                        field.uniqueSelector ? field.uniqueSelector :
                        field.class ? `.${field.class.split(" ").join(".")}` :
                        "";
    
                    return {
                        fieldType,
                        label: field.label,
                        action: actionType,
                        selector,
                        sectionLabel : field.sectionLabel, 
                        sectionSelector : field.sectionSelector
                    };
                });
    
                // 4. Remove already filled
                //const newFields = extractedFields.filter(field => !filledSelectors.has(field.selector));
                const newFields = extractedFields.filter(field =>
                    !filledSelectors.has(field.selector) &&
                    (!field.sectionSelector || !sectionSelectors.has(field.sectionSelector))
                );
    
                if (newFields.length === 0) {
                    console.log("✅ No new fields to fill. Exiting loop.");
                    break;
                }
    
                // console.log("🆕 New fields this round:", newFields);
    
                // 5. Split known/unknown
                const knownFields = [];
                const unknownFields = [];
    
                // for (const field of newFields) {
                //     const matchedValue = getProfileValue(field, profileData.cv_json, newFields);
                //     if (matchedValue) {
                //         knownFields.push({ ...field, value: matchedValue });
                //     } else {
                //         unknownFields.push(field);
                //     }
                // }

                for (const field of newFields) {
                    const valueOrTimes = getProfileValue(field, profileData.cv_json, extractedFields);
                
                    if (field.action === "click" && typeof valueOrTimes === "number") {
                        knownFields.push({ ...field, times: valueOrTimes });
                    } else if (valueOrTimes) {
                        knownFields.push({ ...field, value: valueOrTimes });
                    } else {
                        unknownFields.push(field);
                    }
                }
                

                console.log("🆕 knownFields this round:", knownFields);
                console.log("🆕 unknownFields this round:", unknownFields);

                
    
                // 6. AI fill for unknown fields
                let aiFilledData = [];
                // console.log('formfields',unknownFields)
                // console.log('profiledata',profileData.cv_json)
    
                if (unknownFields.length > 0) {
                    const aiResponse = await fetch("https://genieply.onrender.com/ai-autofill", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ form_fields: unknownFields, profile_data: profileData.cv_json })
                    });
    
                    const aiResult = await aiResponse.json();
                    aiFilledData = aiResult?.fields || [];
                    console.log("🤖 AI Filled:", aiFilledData);
                }
    
                const finalFields = [...knownFields, ...aiFilledData];
                // const finalFields = [...knownFields];
    
                if (finalFields.length === 0) {
                    console.log("⚠️ No values available to autofill. Skipping this round.");
                    break;
                }
    
                // 7. Autofill
                const results = await chrome.scripting.executeScript({
                    target: { tabId },
                    function: executeAgentPlan,
                    args: [knownFields]  // 🚨 YOU NEED TO MAKE executeAgentPlan RETURN list of filled selectors
                });
    
                // const newlyFilled = results?.[0]?.result || [];
                const { filledFields = [], sectionFields = [] } = results?.[0]?.result || {};
    
                if (filledFields.length === 0) {
                    console.log("🛑 No new fields filled by script. Ending loop.");
                    break;
                }
    
                console.log("✅ Newly filled selectors:", filledFields);
                filledFields.forEach(sel => filledSelectors.add(sel));

                console.log("✅ Section selectors:", sectionFields);
                sectionFields.forEach(sec => sectionSelectors.add(sec));

                
            }
            } catch(err){
                console.error("❌ Error during autofill:", err);

            } finally{

            // ✅ After autofill process ends
            document.getElementById("autofilling").style.display = "none";
            document.getElementById("upload-section").classList.remove("hidden");}

    
            console.log("✅ Autofill process complete.");
        });
    });
    

    function executeAgentPlan(planSteps) {
        
        console.log("🤖 Executing AI Agent Plan...");

        let filledFields = new Set();
        let sectionFields = new Set();
    
        for (const step of planSteps) {
            try {
                const { action, selector,sectionSelector, value, times } = step;
                const element = document.querySelector(selector);
    
                if (!element) {
                    console.warn(`⚠️ Element not found for selector: ${selector}`);
                    continue;
                }

                if (action === "type") {
                    element.focus();
                
                    // Use the correct native value setter depending on the element type
                    const prototype = Object.getPrototypeOf(element);
                    const descriptor = Object.getOwnPropertyDescriptor(prototype, "value");
                
                    if (descriptor && descriptor.set) {
                        descriptor.set.call(element, value);
                    } else {
                        element.value = value; // Fallback
                    }
                
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                
                    console.log(`⌨️ Typed '${value}' into: ${selector}`);
                    filledFields.add(selector);
                }
    
                else if (action === "select") {
                    const val = value.toLowerCase();
                    const option = Array.from(element.options).find(opt =>
                        opt.text.toLowerCase().includes(val) || opt.value.toLowerCase().includes(val)
                    );
                    if (option) {
                        element.value = option.value;
                        element.dispatchEvent(new Event("change", { bubbles: true }));
                        console.log(`🔽 Selected '${option.value}' in: ${selector}`);
                    }
                    filledFields.add(selector);
                }
    
                else if (action === "check") {
                    element.checked = true;
                    element.dispatchEvent(new Event("change", { bubbles: true }));
                    console.log(`☑️ Checked: ${selector}`);
                    filledFields.add(selector);
                }
                else if (action === "click") {
                    const repeat = times ;

                    if (repeat <= 0) {
                        console.log(`⛔ Skipping click on ${selector} (times = ${repeat})`);
                        continue;
                    }
                    
                    for (let i = 0; i < repeat; i++) {
                        element.click();
                        // await new Promise(resolve => setTimeout(resolve, 500));
                    }
                    filledFields.add(selector);
                    sectionFields.add(sectionSelector);
                }
                console.log('filledFields',filledFields)
    
            } catch (err) {
                console.error("❌ Error executing step:", step, err);
            }
        }
    
        console.log("✅ AI Agent Execution Complete");
        // return Array.from(filledFields);
        return {
            filledFields: Array.from(filledFields),
            sectionFields: Array.from(sectionFields)
        };
    }

    function extractFormFieldsDirectly() {
        console.log("🔍 Extracting form fields...");
    
        const inputs = document.querySelectorAll("input, textarea, select, button");
        let formStructure = [];
    
        inputs.forEach(field => {
            let label = "";
            let fieldId = field.id || field.name || "";
    
            // Try to find associated label
            if (fieldId) {
                let directLabel = document.querySelector(`label[for="${fieldId}"]`);
                if (directLabel) {
                    label = directLabel.innerText.trim();
                }
            }
    
            // Check for wrapping label
            let wrapperLabel = field.closest("label");
            if (wrapperLabel && !label) {
                label = wrapperLabel.innerText.trim();
            }
    
            // Look for aria-label
            if (!label && field.hasAttribute("aria-label")) {
                label = field.getAttribute("aria-label").trim();
            }
    
            // Check aria-labelledby
            if (!label && field.hasAttribute("aria-labelledby")) {
                let labelElement = document.getElementById(field.getAttribute("aria-labelledby"));
                if (labelElement) {
                    label = labelElement.innerText.trim();
                }
            }
    
            // Fallback: check for nearby text in a div
            if (!label) {
                let parentDiv = field.closest("div");
                if (parentDiv) {
                    let possibleLabel = parentDiv.querySelector("span, strong, b");
                    if (possibleLabel) {
                        label = possibleLabel.innerText.trim();
                    }
                }
            }
    
            // Last resort: use placeholder or button text
            if (!label) {
                if (field.placeholder) {
                    label = field.placeholder.trim();
                } else if (field.tagName.toLowerCase() === "button") {
                    label = field.innerText.trim();
                }
            }
    
            // Push all types including radio & button
            const fieldType = field.type?.toLowerCase() || field.tagName.toLowerCase();

            // Inside formStructure.push({...}), add:
            let section = field.closest('[role="group"][aria-labelledby]');
            let sectionLabel = section ? section.getAttribute("aria-labelledby") : "";

            let uniqueSelector = "";
            if (sectionLabel && field.tagName.toLowerCase() === "button" && label.toLowerCase() === "add") {
                uniqueSelector = `[aria-labelledby="${sectionLabel}"] button`;
            }

            // const key = (field.id || field.name || label || field.className || field.placeholder || field.type).toLowerCase().trim();

            let sectionHeading = sectionLabel ? document.getElementById(sectionLabel)?.innerText.trim() : "";
            let sectionSelector = sectionLabel ? `#${sectionLabel}` : "";

    
            formStructure.push({
                name: field.name || "",
                id: field.id || "",
                class:field.className,
                label: label,
                type: field.tagName.toLowerCase(), // input, textarea, select, button
                fieldType: fieldType, // checkbox, radio, text, etc.
                uniqueSelector: uniqueSelector || "",
                sectionLabel: sectionHeading,
                sectionSelector: sectionSelector
            });

            
        });
    
        console.log("📌 Extracted Form Structure:", formStructure);
        return formStructure;
    }

    function getProfileValue(field, profile, allFields = []) {

        const fieldText = `${field.name} ${field.label} ${field.sectionLabel || ""} ${field.id || ""}`.toLowerCase();
        console.log(fieldText)
        // Handle repeatable section add-buttons first
        if (action === "click" && fieldText == 'add') {
            const section = identifyRepeatableSection(field); // 'education', 'experience', or 'certifications'

            if (section && Array.isArray(profile[section])) {
                const profileCount = profile[section].length;

                // Detect how many are already present in form
                const existingCount = countExistingEntries(section, allFields);
                const timesToClick = Math.max(0, profileCount - existingCount);

                return timesToClick;
            }

            return 0; // Fallback if section not detected or empty
        }
            
        let value = "";
    
        // 🔹 Parse name
        const fullNameParts = (profile.name || "").trim().split(/\s+/);
        let firstName = "n/a", middleName = "n/a", lastName = "n/a";
        if (fullNameParts.length === 1) firstName = fullNameParts[0];
        else if (fullNameParts.length === 2) [firstName, lastName] = fullNameParts;
        else if (fullNameParts.length > 2) {
            firstName = fullNameParts[0];
            middleName = fullNameParts.slice(1, -1).join(" ");
            lastName = fullNameParts[fullNameParts.length - 1];
        }
    
        const fieldMappings = {
            "email": profile.contact?.email || "",
            "phone": profile.contact?.phone || "",
            "location": profile.contact?.location || "",
            "firstname": firstName,
            "middlename": middleName,
            "lastname": lastName,
            "skills": profile.skills?.join(", ") || "",
        };
    
        const keywordMappings = {
            email: ["email", "e-mail", "contact email", "email address"],
            phone: ["phone", "mobile", "contact number"],
            firstname: ["first name", "firstname", "given name"],
            middlename: ["middle name", "middlename"],
            lastname: ["last name", "lastname", "surname"],
            skills: ["skills", "expertise", "abilities"]
        };
    
        // const fieldText = `${field.name} ${field.label} ${field.sectionLabel || ""} ${field.id || ""}`.toLowerCase();
    
        // 🔹 Basic match
        if (matchesKeyword(fieldText, keywordMappings["email"])) return fieldMappings["email"];
        if (matchesKeyword(fieldText, keywordMappings["firstname"])) return firstName;
        if (matchesKeyword(fieldText, keywordMappings["middlename"])) return middleName;
        if (matchesKeyword(fieldText, keywordMappings["lastname"])) return lastName;
    
        // 🔹 Experience
        if (fieldText.includes("experience")) {
            const match = fieldText.match(/experience\s*(\d+)/);
            const index = match ? parseInt(match[1]) - 1 : -1;
            const experience = profile.experience?.[index];
            if (experience) {
                if (fieldText.includes("title") || fieldText.includes("position")) return experience.title || "";
                if (fieldText.includes("company") || fieldText.includes("employer")) return experience.company || "";
                if (fieldText.includes("location")) return experience.location || "";
                if (fieldText.includes("year") || fieldText.includes("start")) return experience.year || "";
                if (fieldText.includes("domain")) return experience.domain || "";
                if (fieldText.includes("responsibility") || fieldText.includes("description")) {
                    return experience.responsibilities?.join("; ") || "";
                }
            }
        }
    
        // 🔹 Education
        if (fieldText.includes("education")) {
            const match = fieldText.match(/education\s*(\d+)/);
            const index = match ? parseInt(match[1]) - 1 : -1;
            const education = profile.education?.[index];
            if (education) {
                if (fieldText.includes("degree")) return education.degree || "";
                if (fieldText.includes("institution") || fieldText.includes("school") || fieldText.includes("college")) return education.institution || "";
                if (fieldText.includes("location")) return education.location || "";
                if (fieldText.includes("year")) return education.year || "";
                if (fieldText.includes("grade") || fieldText.includes("gpa")) return education.grade || "";
            }
        }
    
        // 🔹 Certifications (empty in your example, but structure is ready)
        if (fieldText.includes("certification")) {
            const match = fieldText.match(/certification\s*(\d+)/);
            const index = match ? parseInt(match[1]) - 1 : -1;
            const cert = profile.certifications?.[index];
            if (cert) {
                if (fieldText.includes("name")|| fieldText.includes("certification")) return cert.name || "";
                if (fieldText.includes("issuer")) return cert.issuer || "";
                if (fieldText.includes("date")) return cert.date || "";
            }
        }
    
        // 🔹 Try fallback keyword mapping
        Object.keys(fieldMappings).forEach(key => {
            if (matchesKeyword(fieldText, keywordMappings[key] || [])) {
                value = fieldMappings[key];
            }
        });
    
        return value || "";
    }
    
    function matchesKeyword(text, keywords) {
        return keywords.some(keyword => text.includes(keyword.toLowerCase()));
    }

    function identifyRepeatableSection(field) {
        const fieldText = `${field.name} ${field.label} ${field.sectionLabel || ""}`.toLowerCase();
    
        if (fieldText.includes("education")) return "education";
        if (fieldText.includes("experience")) return "experience";
        if (fieldText.includes("certification")) return "certifications";
    
        return null;
    }
    
    function countExistingEntries(section, fields) {
        let identifierKeyword = "";
    
        switch (section) {
            case "education":
                identifierKeyword = "degree";
                break;
            case "experience":
                identifierKeyword = "title";
                break;
            case "certifications":
                identifierKeyword = "certification"; // Adjust if structure changes
                break;
        }
    
        const count = fields.filter(f => {
            const text = `${f.name} ${f.label} ${f.sectionLabel || ""}`.toLowerCase();
            return text.includes(section) && text.includes(identifierKeyword);
        }).length;
    
        return count;
    }
    
    

    // function getProfileValue(field, profile) {
    //     let value = null;
    
    //     // **🔹 Improved Name Parsing Logic**
    //     const fullNameParts = profile.name?.trim().split(/\s+/) || [];
    //     let firstName = "n/a", middleName = "n/a", lastName = "n/a";
    
    //     if (fullNameParts.length === 1) {
    //         firstName = fullNameParts[0];
    //     } else if (fullNameParts.length === 2) {
    //         [firstName, lastName] = fullNameParts;
    //     } else if (fullNameParts.length > 2) {
    //         firstName = fullNameParts[0];
    //         lastName = fullNameParts[fullNameParts.length - 1];
    //         middleName = fullNameParts.slice(1, -1).join(" ");
    //     }
    //     // console.log('NAMES', firstName, middleName, lastName);

    //     // console.log('EXPERIENCE', profile.experience);
    
    //     // **🔹 Fix: Standard Field Mappings**
    //     const fieldMappings = {
    //         "email": profile.contact?.email,
    //         "phone": profile.contact?.phone,
    //         "location": profile.contact?.location,
    //         "firstname": firstName,
    //         "middlename": middleName,
    //         "lastname": lastName,
    //         "skills": profile.skills?.join(", ") || "",
            
    //     };
    
    //     // **🔹 Fix: Improved Keyword Mapping for More Flexibility**
    //     const keywordMappings = {
    //         "email": ["email", "e-mail", "contact email", "email address", "work email"],
    //         "phone": ["phone number", "mobile", "contact number", "telephone"],
    //         "firstname": ["first name", "firstname", "given name", "fname"],
    //         "middlename": ["middle name", "middlename"],
    //         "lastname": ["last name", "lastname", "surname"],
    //         "skills": ["skills", "expertise", "abilities"]
    //     };
    
    //     // **🔹 Fix: Normalize Field Text for Matching**
    //     let fieldText = `${field.name} ${field.label} ${field.sectionLabel}${field.id || ""}`.toLowerCase().trim();
    
    //     // **🔹 Fix: Prioritize Email Matching to Avoid Conflicts**
    //     if (matchesKeyword(fieldText, keywordMappings["email"])) {
    //         return fieldMappings["email"];
    //     }
    
    //     // **🔹 Fix: Name Handling to Ensure Correct Assignment**
    //     if (matchesKeyword(fieldText, keywordMappings["firstname"])) return firstName;
    //     if (matchesKeyword(fieldText, keywordMappings["middlename"])) return middleName;
    //     if (matchesKeyword(fieldText, keywordMappings["lastname"])) return lastName;
    
    //     // **🔹 Fix: Match Other Profile Fields Dynamically**
    //     Object.keys(fieldMappings).forEach(key => {
    //         if (matchesKeyword(fieldText, keywordMappings[key] || [])) {
    //             value = fieldMappings[key];
    //         }
    //     });
    
    //     return value || ""; // Ensure function always returns a valid string
    // }
    
    // // // **🔹 Helper Function: Checks if Field Matches a Keyword**
    // function matchesKeyword(fieldText, keywords) {
    //     fieldText = fieldText.toLowerCase(); // Convert fieldText to lowercase for case-insensitive matching
    //     return Array.isArray(keywords) && keywords.some(keyword => fieldText.includes(keyword.toLowerCase()));
    // }
    

    
    document.getElementById("go-back").addEventListener("click", function () {
        // Hide the profile section
        document.getElementById("profile-section").classList.add("hidden");
    
        // Show the upload section
        document.getElementById("upload-section").classList.remove("hidden");
    });  
    
    //LOTS TO WORK ON

});