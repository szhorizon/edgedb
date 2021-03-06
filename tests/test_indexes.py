#
# This source file is part of the EdgeDB open source project.
#
# Copyright 2016-present MagicStack Inc. and the EdgeDB authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


from edb.testbase import server as tb


class TestIndexes(tb.DDLTestCase):

    async def test_index_01(self):
        await self.con.execute(r"""
            # setup delta
            CREATE MIGRATION test::d1 TO {
                type Person {
                    property first_name -> str;
                    property last_name -> str;

                    index name_index on ((__subject__.first_name,
                                          __subject__.last_name));
                };

                type Person2 extending Person;
            };

            COMMIT MIGRATION test::d1;
        """)

        await self.assert_query_result(
            r"""
                SELECT
                    schema::ObjectType {
                        indexes: {
                            expr
                        }
                    }
                FILTER schema::ObjectType.name = 'test::Person';
            """,
            [{
                'indexes': [{
                    'expr': 'SELECT (test::Person.first_name, '
                            'test::Person.last_name)'
                }]
            }],
        )

        await self.con.execute(r"""
            INSERT test::Person {
                first_name := 'Elon',
                last_name := 'Musk'
            };
        """)

        await self.assert_query_result(
            r"""
                WITH MODULE test
                SELECT
                    Person {
                        first_name
                    }
                FILTER
                    Person.first_name = 'Elon' AND Person.last_name = 'Musk';
            """,
            [{
                'first_name': 'Elon'
            }]
        )

    async def test_index_02(self):
        await self.con.execute(r"""
            # setup delta
            CREATE TYPE test::User {
                CREATE PROPERTY title -> str;
                CREATE INDEX title_name ON (__subject__.title);
            };
        """)

        await self.assert_query_result(
            r"""
                SELECT
                    schema::ObjectType {
                        indexes: {
                            expr
                        }
                    }
                FILTER .name = 'test::User';
            """,
            [{
                'indexes': [{
                    'expr': 'SELECT test::User.title'
                }]
            }],
        )

        # simply test that the type can be dropped
        await self.con.execute(r"""
            DROP TYPE test::User;
        """)
