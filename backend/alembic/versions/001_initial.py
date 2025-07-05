from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'exams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('duration', sa.Integer(), nullable=False),
        sa.Column('total_score', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'questions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('exam_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('options', sa.Text(), nullable=True),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('analysis', sa.Text(), nullable=True),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('knowledge_point', sa.String(100), nullable=False),
        sa.Column('difficulty', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['exam_id'], ['exams.id'], ),
        sa.PrimaryKeyConstraint('id')
    )