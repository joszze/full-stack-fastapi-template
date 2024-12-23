"""chat model fix

Revision ID: fffa2f0fef37
Revises: 01e3c35dbfdd
Create Date: 2024-11-26 17:08:17.087387

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'fffa2f0fef37'
down_revision = '01e3c35dbfdd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chatmessage', sa.Column('author_alias', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('chatmessage', 'author_alias')
    # ### end Alembic commands ###
