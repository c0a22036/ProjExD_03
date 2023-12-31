import random
import sys
import time
import math
import pygame as pg


WIDTH = 1600  #  ゲームウィンドウの幅
HEIGHT = 900  #  ゲームウィンドウの高さ
NUM_OF_BOMBS = 5


def check_bound(area: pg.Rect, obj: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内か画面外かを判定し，真理値タプルを返す
    引数1 area：画面SurfaceのRect
    引数2 obj：オブジェクト（爆弾，こうかとん）SurfaceのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj.left < area.left or area.right < obj.right:  # 横方向のはみ出し判定
        yoko = False
    if obj.top < area.top or area.bottom < obj.bottom:  # 縦方向のはみ出し判定
        tate = False
    return yoko, tate


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    _delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        self._img = pg.transform.flip(  # 左右反転
            pg.transform.rotozoom(  # 2倍に拡大
                pg.image.load(f"ex03/fig/{num}.png"), 
                0, 
                2.0), 
            True, 
            False
        )
        img0 = pg.transform.rotozoom(pg.image.load(f"ex03/fig/{num}.png"), 0, 2.0)
        img1 = pg.transform.flip(img0, True, False)

        self._imgs = {
            (+1, 0): img1,
            (+1, -1): pg.transform.rotozoom(img1, 45, 1.0),
            (0, -1): pg.transform.rotozoom(img1, 90, 1.0),
            (-1, -1): pg.transform.rotozoom(img0, -45, 1.0),
            (-1, 0): img0,
            (-1, +1): pg.transform.rotozoom(img0, 45, 1.0),
            (0, +1): pg.transform.rotozoom(img1, -90, 1.0),
            (+1, +1): pg.transform.rotozoom(img1, -45, 1.0),
        }
        self._img = self._imgs[(+1, 0)]
        self._rct = self._img.get_rect()
        self._rct.center = xy
        self._dire = (+5, 0)  # 向きのタプル

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self._img = pg.transform.rotozoom(pg.image.load(f"ex03/fig/{num}.png"), 0, 2.0)
        screen.blit(self._img, self._rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in self._delta.items():
            if key_lst[k]:
                self._rct.move_ip(mv)
                sum_mv[0] += mv[0]  # 横方向合計
                sum_mv[1] += mv[1]  # 縦方向合計
        if check_bound(screen.get_rect(), self._rct) != (True, True):
            for k, mv in self._delta.items():
                if key_lst[k]:
                    self._rct.move_ip(-mv[0], -mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self._img = self._imgs[tuple(sum_mv)]
        self._dire = tuple(sum_mv)  # 向きの更新
        screen.blit(self._img, self._rct)


class Bomb:
    """
    爆弾に関するクラス
    """
    _coloars = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255 ,0 ,255 ), (0, 255, 255)]
    _dires = [-1, 0, +1]
    def __init__(self):
        """
        爆弾円Surfaceを生成する
        """
        rad = random.randint(10, 50)
        color = random.choice(Bomb._coloars)
        self._img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self._img, color, (rad, rad), rad)
        self._img.set_colorkey((0, 0, 0))
        self._rct = self._img.get_rect()
        self._rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self._vx, self._vy = random.choice(Bomb._dires), random.choice(Bomb._dires)

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself._vx, self._vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(screen.get_rect(), self._rct)
        if not yoko:
            self._vx *= -1
        if not tate:
            self._vy *= -1
        self._rct.move_ip(self._vx, self._vy)
        screen.blit(self._img, self._rct)


class Beam:
    def __init__(self, bird: Bird):
        self._img = pg.image.load("ex03/fig/beam.png")
        self._rct = self._img.get_rect()

        vx, vy = bird._dire
        angle = math.degrees(math.atan2(-vy, vx))
        self._img = pg.transform.rotozoom(self._img, angle, 1.0)

        self._rct.centerx = bird._rct.centerx + bird._rct.width * vx / 5
        self._rct.centery = bird._rct.centery + bird._rct.height * vy / 5

        # ビームの速度を設定する変数
        self._speed = 1

        # ビームの移動量を計算
        self._dx = vx * self._speed
        self._dy = vy * self._speed

    def update(self, screen: pg.Surface):
        self._rct.move_ip(self._dx, self._dy)
        screen.blit(self._img, self._rct)


class Explosion:
    """
    爆発エフェクトに関するクラス
    """
    def __init__(self, bomb_rect: pg.Rect):
        """
        爆発エフェクトの画像リストを生成し、初期設定を行う
        引数 bomb_rect: 爆発した爆弾の矩形情報
        """
        self._images = [
            pg.image.load("ex03/fig/explosion.gif"),
            pg.transform.flip(pg.image.load("ex03/fig/explosion.gif"), True, False),
            pg.transform.flip(pg.image.load("ex03/fig/explosion.gif"), False, True),
            pg.transform.flip(pg.image.load("ex03/fig/explosion.gif"), True, True)
        ]
        self._image_index = 0
        self._rect = self._images[0].get_rect()
        self._rect.center = bomb_rect.center
        self._life = 20  # 爆発の表示時間

    def update(self, screen: pg.Surface):
        """
        爆発エフェクトを更新して描画する
        引数 screen: 画面Surface
        """
        self._life -= 1
        if self._life <= 0:
            return
        self._image_index = (self._image_index + 1) % len(self._images)
        image = self._images[self._image_index]
        screen.blit(image, self._rect)        


class Score:
    def __init__(self):
        self.font = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)
        self.color = (0, 0, 255)
        self.score = 0
        self.img = self.font.render("Score: 0", 0, self.color)
        self.img_rect = self.img.get_rect()
        self.img_rect.bottomleft = (100, HEIGHT - 50)

    def update(self, screen):
        self.img = self.font.render(f"Score: {self.score}", 0, self.color)
        screen.blit(self.img, self.img_rect)

def main():
    pg.init()
    pg.display.set_caption("たたかえ!こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    bg_img = pg.image.load("ex03/fig/pg_bg.jpg")

    bird = Bird(3, (900, 400))
    bombs = [Bomb() for _ in range(NUM_OF_BOMBS)]
    explosions = []
    beams = []  # Beamクラスのインスタンスを格納するリスト

    score = Score()  # スコアクラスのインスタンスを生成

    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                beams.append(Beam(bird))
        tmr += 1
        screen.blit(bg_img, [0, 0])

        for bomb in bombs:
            bomb.update(screen)
            if bird._rct.colliderect(bomb._rct):
                bird.change_img(8, screen)
                pg.display.update()
                time.sleep(1)
                pg.quit()
                sys.exit()

        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)

        for beam in beams:
            beam.update(screen)
            if beam._rct.left < 0 or beam._rct.right > WIDTH or beam._rct.top < 0 or beam._rct.bottom > HEIGHT:
                beams.remove(beam)

        for beam in beams:
            for i, bomb in enumerate(bombs):
                if beam._rct.colliderect(bomb._rct):
                    beams.remove(beam)
                    del bombs[i]
                    bird.change_img(6, screen)
                    explosions.append(Explosion(bomb._rct))
                    score.score += 1  # スコアを1点増やす
                    break

        for explosion in explosions:
            explosion.update(screen)
            if explosion._life <= 0:
                explosions.remove(explosion)

        score.update(screen)  # スコアを更新して描画

        pg.display.update()
        clock.tick(1000)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()

    