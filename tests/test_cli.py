from ygq import User, Dish, Tag, Comment, Order, Shop
from ygq.models import Message


def test_initdb_command(runner):
    result = runner.invoke(args=['initdb'])
    assert 'Initialized database.' in result.output


def test_initdb_command_with_drop(runner):
    result = runner.invoke(args=['initdb', '--drop'], input='y\n')
    assert 'This operation will delete the database, do you want to continue?' in result.output
    assert 'Drop tables.' in result.output


def test_init_command(runner):
    result = runner.invoke(args=['init'])
    assert 'Initializing the database...' in result.output
    assert 'Initializing the roles and permissions...' in result.output
    assert 'Done.' in result.output


def test_forge_command_with_count(runner):
    result = runner.invoke(args=['forge', '--user', '5', '--follow', '10',
                                 '--dish', '10', '--tag', '10', '--collect', '10',
                                 '--comment', '10', '--order', '20', '--shop', '5',
                                 '--message', '20', '--delivery', '20'])

    assert User.query.count() == 5
    assert 'Generating 5 users...' in result.output

    assert 'Generating 10 follows...' in result.output

    assert Dish.query.count() == 10
    assert 'Generating 10 dishes...' in result.output

    assert Tag.query.count() == 10
    assert 'Generating 10 tags...' in result.output

    assert 'Generating 10 collects...' in result.output

    assert Comment.query.count() == 10
    assert 'Generating 10 comments...' in result.output

    assert Order.query.count() == 40
    assert 'Generating 20 orders...' in result.output

    assert Shop.query.count() == 5
    assert 'Generating 5 shops...' in result.output

    assert Message.query.count() == 20
    assert 'Generating 20 messages...' in result.output

    assert 'Generating 20 deliveries...' in result.output

    assert 'Done.' in result.output
