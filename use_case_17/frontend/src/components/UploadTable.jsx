import React from 'react';
import { DataGrid } from '@mui/x-data-grid';
import { Chip, IconButton } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';

export default function UploadTable({
  rows,
  onRemove,
  onDragStart,
  showRemove = true,
  showStatus = true,
  showCovered = false,
}) {

  const columns = [
    {
      field: 'name',
      headerName: 'Name / label',
      flex: 1,
      renderCell: (params) => (
        <span
          draggable={Boolean(onDragStart)}
          onDragStart={(e) => onDragStart?.(e, params.row)}
          style={{ cursor: onDragStart ? 'grab' : undefined }}
        >
          {params.value}
        </span>
      ),
    },
    { field: 'type', headerName: 'Content type', flex: 1 },
    { field: 'description', headerName: 'Description', flex: 2 },
    { field: 'author', headerName: 'Author / source', flex: 1 },
  ];

  if (showCovered) {
    columns.push({
      field: 'covered',
      headerName: 'Covered in Memo',
      width: 140,
      renderCell: (params) => (
        <Chip
          label={params.value ? 'Yes' : 'No'}
          color={params.value ? 'success' : 'default'}
          size="small"
        />
      ),
    });
  }

  if (showStatus) {
    columns.push({
      field: 'status',
      headerName: 'Status',
      width: 140,
      renderCell: (params) => {
        const color =
          params.value === 'Completed'
            ? 'success'
            : params.value === 'Failed'
            ? 'error'
            : 'info';
        return <Chip label={params.value} color={color} size="small" />;
      },
    });
  }

  if (showRemove) {
    columns.push({
      field: 'actions',
      headerName: 'Remove',
      width: 100,
      sortable: false,
      renderCell: (params) =>
        onRemove ? (
          <IconButton
            size="small"
            onClick={() => onRemove(params.id)}
            disabled={params.row.status === 'In progress'}
          >
            <DeleteIcon fontSize="small" />
          </IconButton>
        ) : null,
    });
  }

  return (
    <div style={{ height: 400, width: '100%' }}>
      <DataGrid
        rows={rows}
        columns={columns}
        density="compact"
        disableRowSelectionOnClick
        getRowId={(r) => r.id}
        initialState={{
          pagination: { paginationModel: { pageSize: 20, page: 0 } },
        }}
      />
    </div>
  );
}