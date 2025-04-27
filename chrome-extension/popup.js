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

// -----------------------------------------------------------------------------------    

     
    document.getElementById("autofill-button").addEventListener("click", async function () {
    console.log("🔹 Autofill button clicked!");

    const tabs = await new Promise(resolve => chrome.tabs.query({ active: true, currentWindow: true }, resolve));
    if (!tabs[0]) {
        console.error("❌ No active tab found.");
        return;
    }
    const tabId = tabs[0].id;

    // Step 1: Extract all possible fields
    const extractionResult = await chrome.scripting.executeScript({
        target: { tabId },
        function: extractRelevantFormFields
    });

    const extractedFields = extractionResult[0]?.result || [];
    console.log("📋 Extracted Relevant Fields:", extractedFields);

    if (extractedFields.length === 0) {
        console.error("❌ No fields found to autofill.");
        return;
    }

    // Step 2: Fetch Profile
    const enteredEmail = sessionStorage.getItem("enteredEmail");
    const profileResponse = await fetch(`https://genieply.onrender.com/users/${enteredEmail}`);
    const profileData = await profileResponse.json();

    if (!profileData.cv_json || Object.keys(profileData.cv_json).length === 0) {
        alert("❗ Please upload a CV or fill profile manually.");
        return;
    }
    console.log("✅ Loaded Profile Data");

    // Step 3: Ask AI to Plan Autofill
    const aiResponse = await fetch("https://genieply.onrender.com/ai-autofill", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ form_fields: extractedFields, profile_data: profileData.cv_json })
    });

    const aiData = await aiResponse.json();
    if (!aiData?.form_fields_filled) {
        console.error("❌ Invalid AI response:", aiData);
        return;
    }

    const { click_steps = [], fill_steps = [] } = aiData.form_fields_filled;

    console.log("🖱 Planned Click Steps:", click_steps);
    console.log("⌨️ Planned Fill Steps:", fill_steps);

    // Step 4: Click if needed
    if (click_steps.length > 0) {
        await chrome.scripting.executeScript({
            target: { tabId },
            function: executeClickSteps,
            args: [click_steps]
        });
        console.log("✅ Click Phase Done");
        await new Promise(resolve => setTimeout(resolve, 2000)); // Wait for DOM to update after clicks
    }

    // Step 5: Fill Fields
    await chrome.scripting.executeScript({
        target: { tabId },
        function: executeFillSteps,
        args: [fill_steps]
    });
    console.log("✅ Autofill Completed");
});

// --- Functions injected into page --- //

    function extractRelevantFormFields() {
    console.log("🔍 Extracting relevant fields...");

    const allFields = document.querySelectorAll("input, textarea, select, button");
    const relevantFields = [];

    allFields.forEach(field => {
        const tag = field.tagName.toLowerCase();
        const type = field.type ? field.type.toLowerCase() : tag;
        const id = field.id || "";
        const name = field.name || "";
        const classList = Array.from(field.classList).join(" ");
        let label = "";

        if (id) {
            const labelElement = document.querySelector(`label[for="${id}"]`);
            if (labelElement) label = labelElement.innerText.trim();
        }
        if (!label && field.closest("label")) {
            label = field.closest("label").innerText.trim();
        }
        if (!label && field.hasAttribute("aria-label")) {
            label = field.getAttribute("aria-label").trim();
        }
        if (!label && field.placeholder) {
            label = field.placeholder.trim();
        }
        if (!label && tag === "button") {
            label = field.innerText.trim();
        }

        // Filter out irrelevant buttons or inputs
        const combinedText = (label + " " + name + " " + id + " " + classList).toLowerCase();
        if (/(save|settings|newsletter|subscribe|logout|filter|search)/i.test(combinedText)) {
            return; // skip irrelevant
        }

        relevantFields.push({ tag, type, id, name, label, classList });
    });

    console.log("📋 Relevant Fields Extracted:", relevantFields);
    return relevantFields;
}

    function executeClickSteps(clickSteps) {
    console.log("🖱 Executing Click Steps...");
    clickSteps.forEach(step => {
        const { selector, times = 1 } = step;
        const element = document.querySelector(selector);

        if (!element) {
            console.warn(`⚠️ Cannot find clickable element: ${selector}`);
            return;
        }

        for (let i = 0; i < times; i++) {
            setTimeout(() => {
                element.scrollIntoView({ behavior: "smooth", block: "center" });
                element.click();
                console.log(`🖱 Clicked ${selector}`);
            }, 200 * i);
        }
    });
}

    function executeFillSteps(fillSteps) {
    console.log("⌨️ Executing Fill Steps...");
    fillSteps.forEach(step => {
        const { action, selector, value } = step;
        const element = document.querySelector(selector);

        if (!element) {
            console.warn(`⚠️ Cannot find field to fill: ${selector}`);
            return;
        }

        if (action === "type") {
            element.focus();
            element.value = value;
            element.dispatchEvent(new Event("input", { bubbles: true }));
            element.dispatchEvent(new Event("change", { bubbles: true }));
        } else if (action === "select") {
            const option = Array.from(element.options).find(opt => 
                opt.text.toLowerCase().includes(value.toLowerCase()) ||
                opt.value.toLowerCase().includes(value.toLowerCase())
            );
            if (option) {
                element.value = option.value;
                element.dispatchEvent(new Event("change", { bubbles: true }));
            }
        } else if (action === "check") {
            element.checked = true;
            element.dispatchEvent(new Event("change", { bubbles: true }));
        }
    });
    console.log("✅ Fill Steps Completed");
}
    
// -----------------------------------------------------------------------------------    
    
    

    function getProfileValue(field, profile) {
        let value = null;
    
        // **🔹 Improved Name Parsing Logic**
        const fullNameParts = profile.name?.trim().split(/\s+/) || [];
        let firstName = "n/a", middleName = "n/a", lastName = "n/a";
    
        if (fullNameParts.length === 1) {
            firstName = fullNameParts[0];
        } else if (fullNameParts.length === 2) {
            [firstName, lastName] = fullNameParts;
        } else if (fullNameParts.length > 2) {
            firstName = fullNameParts[0];
            lastName = fullNameParts[fullNameParts.length - 1];
            middleName = fullNameParts.slice(1, -1).join(" ");
        }
        console.log('NAMES', firstName, middleName, lastName);
    
        // **🔹 Fix: Standard Field Mappings**
        const fieldMappings = {
            "email": profile.contact?.email,
            "phone": profile.contact?.phone,
            "location": profile.contact?.location,
            "firstname": firstName,
            "middlename": middleName,
            "lastname": lastName,
            "education": profile.education?.[0]?.degree || "",
            "university": profile.education?.[0]?.institution || "",
            "experience": profile.experience?.[0]?.title || "",
            "company": profile.experience?.[0]?.company || "",
            "jobtitle": profile.experience?.[0]?.title || "",
            "skills": profile.skills?.join(", ") || "",
        };
    
        // **🔹 Fix: Improved Keyword Mapping for More Flexibility**
        const keywordMappings = {
            "email": ["email", "e-mail", "contact email", "email address", "work email"],
            "phone": ["phone", "mobile", "contact number", "telephone"],
            "firstname": ["first name", "firstname", "given name", "fname"],
            "middlename": ["middle name", "middlename"],
            "lastname": ["last name", "lastname", "surname", "lname"],
            "education": ["degree", "qualification", "major"],
            "university": ["university", "college", "school", "institution"],
            "experience": ["job title", "position", "work"],
            "company": ["company", "organization", "employer"],
            "jobtitle": ["title", "role", "position"],
            "skills": ["skills", "expertise", "abilities"]
        };
    
        // **🔹 Fix: Normalize Field Text for Matching**
        let fieldText = `${field.name} ${field.label} ${field.id || ""}`.toLowerCase().trim();
    
        // **🔹 Fix: Prioritize Email Matching to Avoid Conflicts**
        if (matchesKeyword(fieldText, keywordMappings["email"])) {
            return fieldMappings["email"];
        }
    
        // **🔹 Fix: Name Handling to Ensure Correct Assignment**
        if (matchesKeyword(fieldText, keywordMappings["firstname"])) return firstName;
        if (matchesKeyword(fieldText, keywordMappings["middlename"])) return middleName;
        if (matchesKeyword(fieldText, keywordMappings["lastname"])) return lastName;
    
        // **🔹 Fix: Match Other Profile Fields Dynamically**
        Object.keys(fieldMappings).forEach(key => {
            if (matchesKeyword(fieldText, keywordMappings[key] || [])) {
                value = fieldMappings[key];
            }
        });
    
        return value || ""; // Ensure function always returns a valid string
    }
    
    // **🔹 Helper Function: Checks if Field Matches a Keyword**
    function matchesKeyword(fieldText, keywords) {
        fieldText = fieldText.toLowerCase(); // Convert fieldText to lowercase for case-insensitive matching
        return Array.isArray(keywords) && keywords.some(keyword => fieldText.includes(keyword.toLowerCase()));
    }

    
    
    
    
    
    

    function autofillForm(filledFields) {
        console.log("📥 Autofilling form...");
    
        filledFields.forEach(field => {
            let input = document.querySelector(`[name="${field.name}"]`) || document.querySelector(`[id="${field.id}"]`);
    
            if (input) {
                input.value = field.value;
                console.log(`✅ Filled ${field.name || field.id} with ${field.value}`);
            } else {
                console.warn(`⚠️ Could not find input field for ${field.name || field.id}`);
            }
        });
    }

    
    document.getElementById("go-back").addEventListener("click", function () {
        // Hide the profile section
        document.getElementById("profile-section").classList.add("hidden");
    
        // Show the upload section
        document.getElementById("upload-section").classList.remove("hidden");
    });
    

});