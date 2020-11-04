import kaggle_environments.envs.halite.helpers as halite_helpers

NEIGH_LOOKUP_DISTANCE = 5
CELL_HALLITE_TRESHOLD = 100
CARGO_TRESHOLD = 500


def get_dir_to(from_pos, to_pos, size):
    """
    Returns best direction to move from one position (fromPos) to another (toPos)
    Example: If I'm at pos 0 and want to get to pos 55, which direction should I choose?
    """
    from_x, from_y = divmod(from_pos[0], size), divmod(from_pos[1], size)
    to_x, to_y = divmod(to_pos[0], size), divmod(to_pos[1], size)
    if from_y < to_y:
        return halite_helpers.ShipAction.NORTH
    elif from_y > to_y:
        return halite_helpers.ShipAction.SOUTH
    elif from_x < to_x:
        return halite_helpers.ShipAction.EAST
    elif from_x > to_x:
        return halite_helpers.ShipAction.WEST


def get_neighbours(cell, distance):
    starting_cell = cell
    for _ in range(distance):
        starting_cell = starting_cell.north.west

    cell_list = [starting_cell]

    for _ in range(distance * 2):
        cell_list.append(cell_list[-1].east)

    for _ in range(distance * 2):
        cell_list.extend([c.south for c in cell_list[-(distance * 2 + 1):]])

    del cell_list[(distance * 2 + 1) // 2 + 1]

    return cell_list


def agent(obs, config):
    """
    Returns the commands we send to our ships and shipyards
    """
    size = config.size
    board = halite_helpers.Board(obs, config)
    me = board.current_player

    # If we are missing the ship, use first shipyard to spawn a ship.
    if len(me.ships) == 0 and len(me.shipyards) > 0:
        me.shipyards[0].next_action = halite_helpers.ShipyardAction.SPAWN

    # If there are no shipyards, convert first ship into shipyard.
    if len(me.shipyards) == 0 and len(me.ships) > 0:
        me.ships[0].next_action = halite_helpers.ShipAction.CONVERT

    for ship in me.ships:
        if ship.next_action is None:
            if ship.halite < CARGO_TRESHOLD and ship.cell.halite < CELL_HALLITE_TRESHOLD:
                # If cargo is low and halite at current location is also low,
                # move to a nearby cell containing the most halite
                neighbors = get_neighbours(ship.cell, NEIGH_LOOKUP_DISTANCE)
                best = max(neighbors, key=lambda cell: cell.halite)
                if best.halite > ship.cell.halite:
                    ship.next_action = get_dir_to(ship.position, best.position, size)

            elif ship.halite >= CARGO_TRESHOLD and ship.cell.halite < CELL_HALLITE_TRESHOLD:
                # If we got enough cargo AND there's not enough halite on this cell to bother continuing collecting,
                #  move towards shipyard to deposit cargo
                # This prevents unnecesary trips back and forth and we maximize the amount of halite deposited in one go
                ship.next_action = get_dir_to(ship.position, me.shipyards[0].position, size)

            # Finally, if ship.next_action is left to None, that means it's gonna collect

    return me.next_actions
