import uuid

from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship

# Declarative base class
Base = declarative_base()

# Random UUID
def uuid_gen():
	return str(uuid.uuid4())

# an example mapping using the base
class UserInfo(Base):
	__tablename__ = "userinfo"

	user_id = Column(String, primary_key=True)
	display_name = Column(String(20), nullable=True)
	bio = Column(String, nullable=True)
	file_infos = relationship(
		"FileInfo", back_populates='owner', cascade='all, delete-orphan'
	)
	#page_infos = relationship(
	#	"FileInfo", back_populates='owner', cascade='all, delete-orphan'
	#)

	def as_dict(self):
		return {c.name: getattr(self, c.name) for c in self.__table__.columns}

	def __repr__(self):
		return f"UserInfo(user_id={self.user_id!r}, display_name={self.display_name!r})"

class FileInfo(Base):
	__tablename__ = "fileinfo"

	id = Column(String, primary_key=True, default=uuid_gen)
	title = Column(String)
	filename = Column(String, primary_key=True, nullable=False)
	filetype = Column(String, nullable=False)
	c_time = Column(String, nullable=False)
	a_time = Column(String, nullable=False)
	m_time = Column(String, nullable=False)
	size = Column(String, nullable=False)
	show_meta = Column(String, nullable=False)  # Display meta data on view: true/false
	show_owner = Column(String, nullable=False) # Display owner info on view: true/false
	is_visible = Column(String, nullable=False) # Is visible to public
	width = Column(String, nullable=False)
	height = Column(String, nullable=False)
	meta = Column(String)
	thumbnail = Column(String)

	owner_id = Column(Integer, ForeignKey("userinfo.user_id"), nullable=False)
	owner = relationship("UserInfo", back_populates='file_infos')

	def as_dict(self):
		return {c.name: getattr(self, c.name) for c in self.__table__.columns}

	def __repr__(self):
		return f"FileInfo(id={self.id!r}, filename={self.filename!r}, filetype={self.filetype!r}, size={self.size!r}, thumbnail={self.thumbnail!r})"

class PageInfo(Base):
	__tablename__ = "pageinfo"

	id = Column(Integer, primary_key=True)
	page_name = Column(String, nullable=False)
	page_info = Column(String, nullable=False)
	u_time = Column(String, nullable=False)

	owner_id = Column(Integer, ForeignKey("userinfo.user_id"), nullable=False)
	owner = relationship("UserInfo")

	def as_dict(self):
		return {c.name: getattr(self, c.name) for c in self.__table__.columns}

	def __repr__(self):
		return f"PageInfo(id={self.page_name!r}"

if __name__ == '__main__':
	engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)
	Base.metadata.create_all(engine)