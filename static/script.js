document.getElementById('simulationForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const md5 = document.getElementById('md5').value.trim();
    const numGames = document.getElementById('num_games').value.trim();
    const resultsDiv = document.getElementById('results');
    const chartCanvas = document.getElementById('chart');

    resultsDiv.innerHTML = "<p>Đang xử lý...</p>";

    try {
        const response = await fetch('/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ md5, num_games: parseInt(numGames) }),
        });

        const data = await response.json();

        if (response.ok) {
            // Phân loại kết quả Tài và Xỉu
            const taiResults = {};
            const xiuResults = {};

            Object.entries(data.results).forEach(([key, value]) => {
                if (key.includes("Tài")) {
                    taiResults[key.replace(" (Tài)", "")] = value;
                } else if (key.includes("Xỉu")) {
                    xiuResults[key.replace(" (Xỉu)", "")] = value;
                }
            });

            // Tính toán kết quả cuối cùng
            const totalTai = data.total_tai;
            const totalXiu = data.total_xiu;
            const finalResult = totalTai > totalXiu ? "Tài" : totalTai < totalXiu ? "Xỉu" : "Hòa";

            // Hiển thị bảng kết quả
            let output = `<h3>Kết quả</h3>`;
            output += `<table>
                        <thead>
                            <tr>
                                <th>Loại RNG</th>
                                <th>Tài</th>
                                <th>Xỉu</th>
                            </tr>
                        </thead>
                        <tbody>`;

            Object.keys(taiResults).forEach((rng) => {
                output += `<tr>
                            <td>${rng}</td>
                            <td>${taiResults[rng] || 0}</td>
                            <td>${xiuResults[rng] || 0}</td>
                           </tr>`;
            });

            output += `</tbody></table>`;
            output += `<p><strong>Tổng Tài:</strong> ${totalTai}</p>`;
            output += `<p><strong>Tổng Xỉu:</strong> ${totalXiu}</p>`;
            output += `<p class="final-result"><strong>Kết quả cuối cùng:</strong> ${finalResult}</p>`;
            resultsDiv.innerHTML = output;

            // Vẽ biểu đồ
            const labels = Object.keys(taiResults);
            const taiData = Object.values(taiResults);
            const xiuData = Object.values(xiuResults);

            const chartData = {
                labels: labels,
                datasets: [
                    {
                        label: 'Tài',
                        data: taiData,
                        backgroundColor: '#4caf50',
                        borderColor: '#4caf50',
                        borderWidth: 1,
                    },
                    {
                        label: 'Xỉu',
                        data: xiuData,
                        backgroundColor: '#f44336',
                        borderColor: '#f44336',
                        borderWidth: 1,
                    },
                ],
            };

            const config = {
                type: 'bar',
                data: chartData,
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Loại RNG',
                            },
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Số lần xuất hiện',
                            },
                        },
                    },
                },
            };

            if (window.myChart) {
                window.myChart.destroy();
            }
            window.myChart = new Chart(chartCanvas, config);
        } else {
            resultsDiv.innerHTML = `<p style="color: red;">Lỗi: ${data.error}</p>`;
        }
    } catch (err) {
        resultsDiv.innerHTML = `<p style="color: red;">Có lỗi xảy ra!</p>`;
    }
});
