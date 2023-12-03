document.addEventListener('DOMContentLoaded', function() 
{
    // Listener for Generate Wallet Button
    var generateWalletButton = document.getElementById('generateWallet');
    if (generateWalletButton) 
    {
        generateWalletButton.addEventListener('click', function() {
            fetch('/generate_wallet')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('privateKey').value = data.private_key;
                    document.getElementById('publicKey').value = data.public_key;
                    document.getElementById('walletInfo').style.display = 'block';
                });
        });
    }
    

    var transactionForm = document.getElementById('transactionForm');
    if (transactionForm) 
    {
        transactionForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const sender = document.getElementById('sender').value;
            const recipient = document.getElementById('recipient').value;
            const amount = parseFloat(document.getElementById('amount').value); // Convert to float
            const privateKey = document.getElementById('privateKey').value;

            //Validate input fields
            if (!sender || !recipient || !amount || !privateKey) {
                alert('Please fill in all fields.');
                return;
            }
            // Send the transaction to the server
            fetch('/transaction_route', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ sender, recipient, amount, privateKey })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Server responded with an error!');
                }
                return response.json();
            })
            .then(data => {
                alert('Transaction submitted successfully!');
                transactionForm.reset(); // Reset form fields
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to submit the transaction.');
            });
        });
    }

// Listener for Show Blockchain Button
var showBlockchainButton = document.getElementById('showBlockchain');
if (showBlockchainButton) {
    showBlockchainButton.addEventListener('click', function() {
        fetch('/chain')
            .then(response => response.json())
            .then(blocks => {
                var blockchainContainer = document.getElementById('blockchainContainer');
                blockchainContainer.innerHTML = ''; // Clear existing content

                blocks.forEach(block => {
                    var card = document.createElement('div');
                    card.className = 'card mb-4';

                    var cardBody = document.createElement('div');
                    cardBody.className = 'card-body';

                    var cardTitle = document.createElement('h5');
                    cardTitle.className = 'card-title';
                    cardTitle.textContent = 'Block ' + block.index;
                    cardBody.appendChild(cardTitle);

                    // Create a formatted display of block data
                    var cardText = document.createElement('p');
                    cardText.className = 'card-text text-left';
                    cardText.innerHTML = formatBlockData(block);
                    cardBody.appendChild(cardText);

                    card.appendChild(cardBody);
                    blockchainContainer.appendChild(card);
                });
            });
    });
}


    var submitPublicKeyBtn = document.getElementById('submitPublicKey');
    var inputPublicKey = document.getElementById('inputPublicKey');
    if (submitPublicKeyBtn) {
    
    submitPublicKeyBtn.addEventListener('click', function(event) {
        event.preventDefault();

        var publicKey = inputPublicKey.value;
        if (!publicKey) {
            alert('Please enter your public key.');
            return;
        }

        fetch('/fetch_wallet_info', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ publicKey: publicKey })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Server responded with an error!');
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                displayWalletInfo(data);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to fetch wallet information.');
        });
    });
    }
    function displayWalletInfo(data) {
        document.getElementById('publicAddress').textContent = data.publicAddress;
        document.getElementById('balance').textContent = data.balance;
        document.getElementById('transactionHistory').textContent = JSON.stringify(data.transactionHistory, null, 2);
        document.getElementById('walletDetails').style.display = 'block';
    }


});

// Helper Functions
function toggleVisibility(elementId, button) {
    let inputElement = document.getElementById(elementId);
    if (inputElement.type === "password") {
        inputElement.type = "text";
        button.textContent = 'Hide';
    } else {
        inputElement.type = "password";
        button.textContent = 'Show';
    }
}

function copyToClipboard(elementId) {
    let copyText = document.getElementById(elementId);
    let currentType = copyText.type;  // Save the current type of the input field

    // Temporarily set the type to text
    copyText.type = 'text';
    copyText.select();
    document.execCommand('copy');
    // Revert the type back to its original state
    copyText.type = currentType;
}
function displayWalletInfo(data) {
    document.getElementById('publicAddress').textContent = 'Public Address: ' + data.publicAddress;
    document.getElementById('balance').textContent = 'Balance: ' + data.balance;

    var transactionHistoryElement = document.getElementById('transactionHistory');
    transactionHistoryElement.innerHTML = '';

    if (data.transactionHistory && data.transactionHistory.length > 0) {
        data.transactionHistory.forEach(transaction => {
            var transactionElement = document.createElement('div');
            transactionElement.className = 'transaction mb-2 p-2';
            transactionElement.innerHTML = formatTransactionData(transaction);
            transactionHistoryElement.appendChild(transactionElement);
        });
    } else {
        transactionHistoryElement.textContent = 'No transactions found.';
    }

    document.getElementById('walletDetails').style.display = 'block';
}

function formatTransactionData(transaction) {
    return `
        <div><strong>Amount:</strong> <span>${transaction.amount}</span></div>
        <div><strong>Recipient:</strong> <span>${transaction.recipient}</span></div>
        <div><strong>Sender:</strong> <span>${transaction.sender}</span></div>
        
        <div><strong>Signature:</strong> <span>${transaction.signature}</span></div>

    `;
}

function formatBlockData(block) {
    var formattedData = '<strong>Timestamp: </strong> ' + block.timestamp + '<br>';
    formattedData += '<strong>Previous Hash: </strong> ' + block.previous_hash + '<br>';
    formattedData += '<strong>Current Hash: </strong> ' + block.current_hash + '<br>'+'<br>';

    if (Array.isArray(block.data)) {
        block.data.forEach(transaction => {
            formattedData += '<div class="transaction">' + formatTransactionData(transaction) + '</div>';
        });
    } else if (typeof block.data === 'object' && block.data !== null) {
        formattedData += '<div class="transaction">' + formatTransactionData(block.data) + '</div>';
    } else {
        formattedData += '<strong>Data:</strong> ' + JSON.stringify(block.data) + '<br>';
    }
    return formattedData;
}
