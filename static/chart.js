let chartInstance = null;
let lastData = null;

function toggleSpouseFields(){
    const gender = document.getElementById("deceased_gender").value;
    document.getElementById("husband_box").style.display = gender === "أنثى" ? "block" : "none";
    document.getElementById("wives_box").style.display = gender === "ذكر" ? "block" : "none";
}

document.addEventListener("DOMContentLoaded", toggleSpouseFields);

function collectFormData() {
    const gender = document.getElementById("deceased_gender").value;

    return {
        estate: parseFloat(document.getElementById("estate").value),
        deceased_gender: gender,
        husband: gender === "أنثى" && document.getElementById("husband").checked,
        wives: gender === "ذكر" ? parseInt(document.getElementById("wives").value) : 0,
        father: document.getElementById("father").checked,
        mother: document.getElementById("mother").checked,
        sons: parseInt(document.getElementById("sons").value) || 0,
        daughters: parseInt(document.getElementById("daughters").value) || 0,
        brothers: parseInt(document.getElementById("brothers").value) || 0,
        sisters: parseInt(document.getElementById("sisters").value) || 0,
        grandfather: document.getElementById("grandfather").checked,
        grandmother: document.getElementById("grandmother").checked,
        halfbrothers_father: parseInt(document.getElementById("halfbrothers_father").value) || 0,
        halfsisters_father: parseInt(document.getElementById("halfsisters_father").value) || 0
    };
}

function calculate(){
    lastData = collectFormData();

    fetch("/calculate", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(lastData)
    })
    .then(res => res.json())
    .then(data => {
        displayResults(data);
    })
    .catch(err => {
        console.error("Error:", err);
        alert("حدث خطأ في الحساب. يرجى التحقق من البيانات المدخلة.");
    });
}

function displayResults(data) {
    // Show results section
    document.getElementById("results").style.display = "block";
    
    // Scroll to results
    document.getElementById("results").scrollIntoView({ behavior: 'smooth' });
    
    // Display explanation with Ayah
    const exp = document.getElementById("explanation");
    exp.innerHTML = "<h3>📖 تفاصيل الحساب والآيات القرآنية:</h3>";
    
    if (data.explanation && data.explanation.length > 0) {
        data.explanation.forEach(e => {
            exp.innerHTML += `<p>${e}</p>`;
        });
    } else {
        exp.innerHTML += "<p>لم يتم تحديد أي وارثين.</p>";
    }

    // Draw chart if there are values
    if (data.values && data.values.length > 0) {
        drawChart(data);
        displaySummary(data);
    } else {
        document.getElementById("chart").style.display = "none";
        document.getElementById("summaryTable").innerHTML = "<tr><td colspan='2'>لا توجد نتائج للعرض</td></tr>";
    }
}

function drawChart(data){
    const ctx = document.getElementById("chart").getContext("2d");
    if(chartInstance) chartInstance.destroy();

    // Format labels with values
    const labels = data.labels.map((label, index) => {
        return `${label}: ${data.values[index].toFixed(2)}`;
    });

    // Generate colors for pie chart
    const colors = [
        '#667eea', '#764ba2', '#ec4899', '#f59e0b',
        '#10b981', '#06b6d4', '#8b5cf6', '#f97316',
        '#6366f1', '#a855f7', '#d946ef', '#db2777',
        '#06b6d4', '#14b8a6', '#84cc16', '#eab308'
    ];

    chartInstance = new Chart(ctx,{
        type:"doughnut",
        data:{
            labels:labels,
            datasets:[{
                data:data.values,
                backgroundColor:colors.slice(0, data.values.length),
                borderColor:'#fff',
                borderWidth:3
            }]
        },
        options:{
            responsive:true,
            maintainAspectRatio:true,
            plugins:{
                legend:{
                    position:"bottom",
                    labels:{
                        font:{
                            family:"'Tahoma', 'Arial', sans-serif",
                            size:13,
                            weight:'500'
                        },
                        padding:15,
                        usePointStyle:true,
                        pointStyle:'circle'
                    }
                },
                tooltip:{
                    backgroundColor:'rgba(0, 0, 0, 0.8)',
                    titleFont:{
                        family:"'Tahoma', 'Arial', sans-serif",
                        size:13
                    },
                    bodyFont:{
                        family:"'Tahoma', 'Arial', sans-serif",
                        size:12
                    },
                    padding:12,
                    displayColors:true
                }
            }
        }
    });
}

function displaySummary(data) {
    const table = document.getElementById("summaryTable");
    const estate = lastData.estate;
    
    let html = `
        <thead>
            <tr>
                <th>النسبة %</th>
                <th>المبلغ</th>
                <th>الوارث</th>
            </tr>
        </thead>
        <tbody>
    `;
    
    let total = 0;
    data.labels.forEach((label, index) => {
        const amount = data.values[index];
        const percentage = ((amount / estate) * 100).toFixed(2);
        total += amount;
        html += `
            <tr>
                <td>${percentage}%</td>
                <td>${amount.toFixed(2)}</td>
                <td>${label}</td>
            </tr>
        `;
    });
    
    html += `
        <tr class="total-row">
            <td>100%</td>
            <td style="font-weight:bold;">${total.toFixed(2)}</td>
            <td style="font-weight:bold;">الإجمالي</td>
        </tr>
        </tbody>
    `;
    
    table.innerHTML = html;
}

function downloadPDF(){
    if (!lastData) {
        alert("يرجى إجراء الحساب أولاً");
        return;
    }

    fetch("/pdf", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(lastData)
    })
    .then(res => res.blob())
    .then(blob => {
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = "تقرير_المواريث.pdf";
        a.click();
    })
    .catch(err => {
        console.error("Error:", err);
        alert("حدث خطأ في تحميل التقرير");
    });
}

function resetCalculator() {
    document.getElementById("estate").value = "100000";
    document.getElementById("deceased_gender").value = "ذكر";
    document.getElementById("husband").checked = false;
    document.getElementById("wives").value = "0";
    document.getElementById("father").checked = false;
    document.getElementById("mother").checked = false;
    document.getElementById("sons").value = "0";
    document.getElementById("daughters").value = "0";
    document.getElementById("brothers").value = "0";
    document.getElementById("sisters").value = "0";
    document.getElementById("grandfather").checked = false;
    document.getElementById("grandmother").checked = false;
    document.getElementById("halfbrothers_father").value = "0";
    document.getElementById("halfsisters_father").value = "0";
    
    document.getElementById("results").style.display = "none";
    toggleSpouseFields();
}
