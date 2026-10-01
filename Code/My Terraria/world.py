from settings import WORLD_WIDTH, WORLD_HEIGHT, CHUNK_WIDTH, CHUNK_HEIGHT
import tiles

class World:
    def __init__(self, seed=0, creative=False):
        self.seed = seed
        self.creative = creative
        self.chunks = {}
        # Generate initial chunks
        for cx in range(WORLD_WIDTH // CHUNK_WIDTH):
            self.ensure_chunk(cx)

    def ensure_chunk(self, cx):
        if cx not in self.chunks:
            chunk = []
            for y in range(CHUNK_HEIGHT):
                row = []
                for x in range(CHUNK_WIDTH):
                    # Simple terrain: bottom 10 rows are stone, next 5 are dirt, then grass, rest is air
                    if y > CHUNK_HEIGHT - 10:
                        row.append(tiles.STONE)
                    elif y == CHUNK_HEIGHT - 11:
                        row.append(tiles.GRASS)
                    elif y > CHUNK_HEIGHT - 16:
                        row.append(tiles.DIRT)
                    else:
                        row.append(tiles.AIR)
                chunk.append(row)
            self.chunks[cx] = chunk

    def get_tile(self, x, y):
        cx = x // CHUNK_WIDTH
        if cx not in self.chunks:
            self.ensure_chunk(cx)
        chunk = self.chunks[cx]
        lx = x % CHUNK_WIDTH
        ly = y
        if 0 <= lx < CHUNK_WIDTH and 0 <= ly < CHUNK_HEIGHT:
            return chunk[ly][lx]
        return tiles.AIR

    def set_tile(self, x, y, tid):
        cx = x // CHUNK_WIDTH
        if cx not in self.chunks:
            self.ensure_chunk(cx)
        chunk = self.chunks[cx]
        lx = x % CHUNK_WIDTH
        ly = y
        if 0 <= lx < CHUNK_WIDTH and 0 <= ly < CHUNK_HEIGHT:
            chunk[ly][lx] = tid

    def save_modified(self):
        pass             #Saving Function? 