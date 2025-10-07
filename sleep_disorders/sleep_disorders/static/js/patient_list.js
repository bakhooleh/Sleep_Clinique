.patient-list-container {
    max-width: 1400px;
    margin: 0 auto;
}

.search-section {
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: var(--shadow);
    margin: 20px 0;
}

.search-form {
    width: 100%;
}

.search-input-group {
    display: flex;
    gap: 10px;
    align-items: center;
}

.search-input {
    flex: 1;
}

.table-section {
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: var(--shadow);
}

.action-buttons {
    display: flex;
    gap: 5px;
}

.pagination-nav {
    margin-top: 20px;
    display: flex;
    justify-content: center;
}

.pagination {
    display: flex;
    list-style: none;
    padding: 0;
    margin: 0;
    gap: 5px;
}

.page-item {
    display: inline-block;
}

.page-link {
    display: block;
    padding: 8px 12px;
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 4px;
    color: var(--text-dark);
    text-decoration: none;
    transition: all 0.3s ease;
}

.page-link:hover {
    background: var(--light-green);
    border-color: var(--primary-green);
}

.page-item.active .page-link {
    background: var(--primary-green);
    color: white;
    border-color: var(--primary-green);
}

.btn-sm i {
    font-size: 14px;
}

@media (max-width: 768px) {
    .search-input-group {
        flex-direction: column;
    }
    
    .search-input-group .btn {
        width: 100%;
    }
    
    .table-responsive {
        overflow-x: auto;
    }
    
    .action-buttons {
        flex-direction: column;
    }
}
.btn {
background-color: #28a745;
color: white;
padding: 6px 12px;
border: none;
border-radius: 4px;
cursor: pointer;
text-decoration: none;
font-size: 14px;
}

.btn-warning {
background-color: #ffc107;
}

.btn-danger {
background-color: #dc3545;
}

.btn:hover {
opacity: 0.9;
}