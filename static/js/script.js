function updateCount(id, change) {
    const input = document.getElementById(id);
    let value = parseInt(input.value);
    let min = parseInt(input.min);
    let max = input.hasAttribute('max') ? parseInt(input.max) : Infinity;

    // Logic to prevent Husband and Wife being selected together
    if (id === 'husband' && change > 0) {
        const wifeCount = parseInt(document.getElementById('wife').value);
        if (wifeCount > 0) {
            alert('لا يمكن اجتماع الزوج والزوجة في مسألة واحدة (المتوفى إما ذكر أو أنثى).');
            return;
        }
    }
    if (id === 'wife' && change > 0) {
        const husbandCount = parseInt(document.getElementById('husband').value);
        if (husbandCount > 0) {
            alert('لا يمكن اجتماع الزوج والزوجة في مسألة واحدة (المتوفى إما ذكر أو أنثى).');
            return;
        }
    }

    value += change;

    if (value >= min && value <= max) {
        input.value = value;
    }
}

document.getElementById('inheritanceForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const totalEstate = document.getElementById('total_estate').value;
    const heirs = {
        husband: document.getElementById('husband').value,
        wife: document.getElementById('wife').value,
        father: document.getElementById('father').value,
        mother: document.getElementById('mother').value,
        son: document.getElementById('son').value,
        daughter: document.getElementById('daughter').value
    };

    try {
        const response = await fetch('/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                total_estate: totalEstate,
                heirs: heirs
            })
        });

        const data = await response.json();
        displayResults(data);
    } catch (error) {
        console.error('Error:', error);
        alert('حدث خطأ أثناء الحساب. يرجى المحاولة مرة أخرى.');
    }
});

function displayResults(data) {
    const resultsSection = document.getElementById('results');
    const resultsGrid = document.getElementById('resultsGrid');
    const displayTotalEstate = document.getElementById('displayTotalEstate');
    const displayTotalDistributed = document.getElementById('displayTotalDistributed');

    resultsGrid.innerHTML = '';
    
    if (data.results.length === 0) {
        resultsGrid.innerHTML = '<p style="grid-column: 1/-1; text-align: center;">لا يوجد ورثة مستحقون بناءً على المدخلات.</p>';
    } else {
        data.results.forEach(result => {
            const card = document.createElement('div');
            card.className = 'result-card';
            
            // Format numbers nicely
            const formattedAmount = new Intl.NumberFormat('ar-YE', { style: 'currency', currency: 'RYE' }).format(result.total_amount);
            
            card.innerHTML = `
                <div class="heir-name">${result.name} ${result.count > 1 ? '(' + result.count + ')' : ''}</div>
                <div class="heir-share">النسبة: ${result.share_percentage}%</div>
                <div class="heir-amount">${formattedAmount}</div>
            `;
            resultsGrid.appendChild(card);
        });
    }

    displayTotalEstate.textContent = new Intl.NumberFormat('ar-YE', { style: 'currency', currency: 'RYE' }).format(data.total_estate);
    displayTotalDistributed.textContent = new Intl.NumberFormat('ar-YE', { style: 'currency', currency: 'RYE' }).format(data.total_distributed);

    resultsSection.classList.remove('hidden');
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}
