// ✅ Check if JS is loading
console.log("✅ ingredients.js loaded");

// 🔊 sound function
function playSound() {
    const sound = document.getElementById("clickSound");
    if (sound) {
        sound.currentTime = 0;
        sound.play().catch(() => {});
    }
}

// 💥 pop animation
function popEffect(el) {
    if (!el) return;
    el.style.transform = "scale(0.85)";
    setTimeout(() => {
        el.style.transform = "scale(1)";
    }, 150);
}

// ➕ Add ingredient input
function addIngredient() {
    const container = document.getElementById("ingredientsList");

    if (!container) {
        console.error("❌ ingredientsList not found");
        return;
    }

    const input = document.createElement("input");
    input.type = "text";
    input.placeholder = "Enter ingredient 🍓";

    container.appendChild(input);

    playSound();
    popEffect(input);
}

// 🎯 Attach events safely AFTER DOM loads
window.addEventListener("DOMContentLoaded", () => {

    console.log("✅ DOM loaded");

    // Buttons
    document.querySelectorAll("button").forEach(btn => {
        btn.addEventListener("click", () => {
            playSound();
            popEffect(btn);
        });
    });

    // Inputs
    document.querySelectorAll("input").forEach(input => {
        input.addEventListener("focus", () => {
            playSound();
            popEffect(input);
        });
    });

    // Dropdowns
    document.querySelectorAll("select").forEach(select => {
        select.addEventListener("change", () => {
            playSound();
            popEffect(select);
        });
    });
});


// 🚀 SAVE INGREDIENTS + GO TO NEXT PAGE
function goToMore() {

    const inputs = document.querySelectorAll("#ingredientsList input");

    let ingredients = [];

    inputs.forEach(inp => {
        const value = inp.value.trim();

        if (value !== "") {
            ingredients.push(value.toLowerCase());
        }
    });

    console.log("📦 Ingredients saved:", ingredients);

    // ❗ Prevent empty submission
    if (ingredients.length === 0) {
        alert("⚠️ Please enter at least one ingredient!");
        return;
    }

    // Get food type
    const foodTypeSelect = document.querySelector("select");
    let foodType = foodTypeSelect ? foodTypeSelect.value : "";
    if (foodType.includes("Veg")) {
        foodType = "veg";
    } else if (foodType.includes("Non-Veg")) {
        foodType = "non-veg";
    } else {
        foodType = "";
    }

    // Get flavor
    const flavorSelect = document.querySelectorAll("select")[1];
    let flavor = flavorSelect ? flavorSelect.value : "";
    if (flavor.includes("Sweet")) {
        flavor = "sweet";
    } else if (flavor.includes("Spicy")) {
        flavor = "spicy";
    } else if (flavor.includes("Sour")) {
        flavor = "sour";
    } else if (flavor.includes("Bitter")) {
        flavor = "bitter";
    } else {
        flavor = "";
    }

    console.log("🍽️ Food type:", foodType);
    console.log("🌶️ Flavor:", flavor);

    // Save to localStorage
    localStorage.setItem("ingredients", JSON.stringify(ingredients));
    localStorage.setItem("foodType", foodType);
    localStorage.setItem("flavor", flavor);

    // Go to next page
    window.location.href = "more.html";
}


// ➡️ OPTIONAL: Go to result page
function goToResult() {
    window.location.href = "result.html";
}