"""Add receipt parsing fields

Revision ID: add_receipt_parsing_fields
Revises: 
Create Date: 2025-09-06 06:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_receipt_parsing_fields'
down_revision = None
depends_on = None


def upgrade():
    """Add parsing-related fields to receipts table."""
    # Make file_path nullable (since we might not keep files after parsing)
    op.alter_column('receipts', 'file_path', nullable=True)
    
    # Add new file metadata fields
    op.add_column('receipts', sa.Column('original_filename', sa.String(255), nullable=True))
    op.add_column('receipts', sa.Column('file_size', sa.Integer(), nullable=True))
    op.add_column('receipts', sa.Column('mime_type', sa.String(100), nullable=True))
    
    # Add new parsed fields
    op.add_column('receipts', sa.Column('vat_rate', sa.Numeric(5,2), nullable=True))
    op.add_column('receipts', sa.Column('invoice_number', sa.String(100), nullable=True))
    op.add_column('receipts', sa.Column('payment_method', sa.String(50), nullable=True))
    op.add_column('receipts', sa.Column('merchant_address', sa.Text(), nullable=True))
    op.add_column('receipts', sa.Column('merchant_tax_id', sa.String(50), nullable=True))
    
    # Add parsing metadata fields
    op.add_column('receipts', sa.Column('parsing_status', sa.String(50), nullable=True))
    op.add_column('receipts', sa.Column('parsing_confidence', sa.Numeric(5,2), nullable=True))
    op.add_column('receipts', sa.Column('parsed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('receipts', sa.Column('ocr_text', sa.Text(), nullable=True))
    
    # Add user fields
    op.add_column('receipts', sa.Column('verified', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('receipts', sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
    op.add_column('receipts', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))


def downgrade():
    """Remove parsing-related fields from receipts table."""
    # Remove new columns
    op.drop_column('receipts', 'updated_at')
    op.drop_column('receipts', 'created_at')
    op.drop_column('receipts', 'verified')
    op.drop_column('receipts', 'ocr_text')
    op.drop_column('receipts', 'parsed_at')
    op.drop_column('receipts', 'parsing_confidence')
    op.drop_column('receipts', 'parsing_status')
    op.drop_column('receipts', 'merchant_tax_id')
    op.drop_column('receipts', 'merchant_address')
    op.drop_column('receipts', 'payment_method')
    op.drop_column('receipts', 'invoice_number')
    op.drop_column('receipts', 'vat_rate')
    op.drop_column('receipts', 'mime_type')
    op.drop_column('receipts', 'file_size')
    op.drop_column('receipts', 'original_filename')
    
    # Restore file_path as not nullable
    op.alter_column('receipts', 'file_path', nullable=False)
